package dev.plpssnt.unolab;

import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.hardware.usb.UsbConstants;
import android.hardware.usb.UsbDevice;
import android.hardware.usb.UsbDeviceConnection;
import android.hardware.usb.UsbEndpoint;
import android.hardware.usb.UsbInterface;
import android.hardware.usb.UsbManager;
import android.os.Build;
import android.util.Base64;

import androidx.core.content.ContextCompat;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

/**
 * Collegamento USB con la UNO (porta seriale CDC-ACM del chip ATmega16U2), senza librerie esterne.
 * Nella WebView di Android non esiste WebUSB: questo plugin fa le stesse cose del driver WebUSB della PWA.
 *
 * Metodi JS (window.Capacitor, plugin "UnoSerial"):
 *   connetti({chiedi})    -> {ok, nome, motivo}   chiedi=true mostra la richiesta di permesso
 *   segnali({dtr, rts})                           linee DTR/RTS (DTR fa ripartire la UNO)
 *   scrivi({b64})                                 invia byte (base64)
 *   chiudi()
 * Eventi: "dati" {b64}, "staccato", "attaccato"
 */
@CapacitorPlugin(name = "UnoSerial")
public class UnoSerialPlugin extends Plugin {

    private static final String AZIONE_PERMESSO = "dev.plpssnt.unolab.PERMESSO_USB";
    private static final int BAUD = 115200;

    private UsbManager usb;
    private UsbDevice dev;
    private UsbDeviceConnection conn;
    private UsbInterface comm, data;
    private UsbEndpoint epIn, epOut;
    private Thread lettore;
    private volatile boolean aperto = false;
    private PluginCall inAttesa;

    private final BroadcastReceiver ricevitore = new BroadcastReceiver() {
        @Override
        public void onReceive(Context ctx, Intent intent) {
            String a = intent.getAction();
            UsbDevice d = intent.getParcelableExtra(UsbManager.EXTRA_DEVICE);
            if (AZIONE_PERMESSO.equals(a)) {
                PluginCall call = inAttesa;
                inAttesa = null;
                if (call == null) return;
                if (d != null && usb.hasPermission(d)) apri(d, call);
                else risposta(call, false, "permesso negato");
            } else if (UsbManager.ACTION_USB_DEVICE_DETACHED.equals(a)) {
                if (d != null && dev != null && d.getDeviceId() == dev.getDeviceId()) {
                    chiudiTutto();
                    notifyListeners("staccato", new JSObject());
                }
            } else if (UsbManager.ACTION_USB_DEVICE_ATTACHED.equals(a)) {
                notifyListeners("attaccato", new JSObject());
            }
        }
    };

    @Override
    public void load() {
        usb = (UsbManager) getContext().getSystemService(Context.USB_SERVICE);
        IntentFilter f = new IntentFilter();
        f.addAction(AZIONE_PERMESSO);
        f.addAction(UsbManager.ACTION_USB_DEVICE_DETACHED);
        f.addAction(UsbManager.ACTION_USB_DEVICE_ATTACHED);
        ContextCompat.registerReceiver(getContext(), ricevitore, f, ContextCompat.RECEIVER_NOT_EXPORTED);
    }

    @Override
    protected void handleOnDestroy() {
        chiudiTutto();
        try { getContext().unregisterReceiver(ricevitore); } catch (Exception ignored) { }
    }

    /** La prima periferica USB che ha un'interfaccia dati CDC (classe 10): la UNO. */
    private UsbDevice trova() {
        for (UsbDevice d : usb.getDeviceList().values()) {
            for (int i = 0; i < d.getInterfaceCount(); i++) {
                if (d.getInterface(i).getInterfaceClass() == UsbConstants.USB_CLASS_CDC_DATA) return d;
            }
        }
        return null;
    }

    @PluginMethod
    public void connetti(PluginCall call) {
        boolean chiedi = call.getBoolean("chiedi", true);
        if (aperto) chiudiTutto();
        UsbDevice d = trova();
        if (d == null) { risposta(call, false, "nessuna scheda collegata"); return; }
        if (usb.hasPermission(d)) { apri(d, call); return; }
        if (!chiedi) { risposta(call, false, "serve il permesso"); return; }
        inAttesa = call;
        Intent i = new Intent(AZIONE_PERMESSO).setPackage(getContext().getPackageName());
        int flag = Build.VERSION.SDK_INT >= Build.VERSION_CODES.S ? PendingIntent.FLAG_MUTABLE : 0;
        PendingIntent pi = PendingIntent.getBroadcast(getContext(), 0, i, flag | PendingIntent.FLAG_UPDATE_CURRENT);
        usb.requestPermission(d, pi);
    }

    private void apri(UsbDevice d, PluginCall call) {
        try {
            comm = null; data = null; epIn = null; epOut = null;
            for (int i = 0; i < d.getInterfaceCount(); i++) {
                UsbInterface it = d.getInterface(i);
                if (it.getInterfaceClass() == UsbConstants.USB_CLASS_COMM && comm == null) comm = it;
                if (it.getInterfaceClass() == UsbConstants.USB_CLASS_CDC_DATA && data == null) data = it;
            }
            if (data == null) { risposta(call, false, "non è una porta seriale"); return; }
            for (int i = 0; i < data.getEndpointCount(); i++) {
                UsbEndpoint e = data.getEndpoint(i);
                if (e.getType() != UsbConstants.USB_ENDPOINT_XFER_BULK) continue;
                if (e.getDirection() == UsbConstants.USB_DIR_IN) epIn = e; else epOut = e;
            }
            conn = usb.openDevice(d);
            if (conn == null) { risposta(call, false, "impossibile aprire la scheda"); return; }
            if (comm != null) conn.claimInterface(comm, true);
            if (!conn.claimInterface(data, true)) { chiudiTutto(); risposta(call, false, "scheda occupata da un'altra app"); return; }
            // SET_LINE_CODING: 115200 baud, 1 bit di stop, nessuna parità, 8 bit
            byte[] lc = { (byte) (BAUD & 0xff), (byte) ((BAUD >> 8) & 0xff), (byte) ((BAUD >> 16) & 0xff), (byte) ((BAUD >> 24) & 0xff), 0, 0, 8 };
            conn.controlTransfer(0x21, 0x20, 0, indiceComm(), lc, lc.length, 1000);
            dev = d;
            aperto = true;
            avviaLettore();
            JSObject r = new JSObject();
            r.put("ok", true);
            r.put("nome", d.getProductName() != null ? d.getProductName() : "UNO");
            call.resolve(r);
        } catch (Exception e) {
            chiudiTutto();
            risposta(call, false, e.getMessage());
        }
    }

    /** Chiamato da MainActivity quando Android segnala una scheda appena collegata. */
    public void schedaAttaccata() {
        notifyListeners("attaccato", new JSObject());
    }

    private int indiceComm() { return comm != null ? comm.getId() : 0; }

    private void avviaLettore() {
        final UsbDeviceConnection c = conn;
        final UsbEndpoint in = epIn;
        lettore = new Thread(() -> {
            byte[] buf = new byte[in.getMaxPacketSize() > 0 ? Math.max(64, in.getMaxPacketSize()) : 64];
            while (aperto) {
                int n = c.bulkTransfer(in, buf, buf.length, 200);
                if (n > 0) {
                    JSObject o = new JSObject();
                    o.put("b64", Base64.encodeToString(buf, 0, n, Base64.NO_WRAP));
                    notifyListeners("dati", o);
                }
            }
        }, "UnoSerial-lettore");
        lettore.setDaemon(true);
        lettore.start();
    }

    @PluginMethod
    public void segnali(PluginCall call) {
        if (!aperto) { call.reject("non collegato"); return; }
        int v = (call.getBoolean("dtr", false) ? 1 : 0) | (call.getBoolean("rts", false) ? 2 : 0);
        int r = conn.controlTransfer(0x21, 0x22, v, indiceComm(), null, 0, 1000);
        if (r < 0) call.reject("segnali non inviati"); else call.resolve();
    }

    @PluginMethod
    public void scrivi(PluginCall call) {
        if (!aperto) { call.reject("non collegato"); return; }
        byte[] b = Base64.decode(call.getString("b64", ""), Base64.DEFAULT);
        int fatto = 0;
        while (fatto < b.length) {
            int n = Math.min(b.length - fatto, 4096);
            byte[] pezzo = new byte[n];
            System.arraycopy(b, fatto, pezzo, 0, n);
            int r = conn.bulkTransfer(epOut, pezzo, n, 2000);
            if (r < 0) { call.reject("scrittura non riuscita"); return; }
            fatto += r;
        }
        call.resolve();
    }

    @PluginMethod
    public void chiudi(PluginCall call) {
        chiudiTutto();
        call.resolve();
    }

    private void chiudiTutto() {
        aperto = false;
        if (lettore != null) { try { lettore.join(500); } catch (InterruptedException ignored) { } lettore = null; }
        if (conn != null) {
            try { if (data != null) conn.releaseInterface(data); } catch (Exception ignored) { }
            try { if (comm != null) conn.releaseInterface(comm); } catch (Exception ignored) { }
            conn.close();
            conn = null;
        }
        dev = null;
    }

    private void risposta(PluginCall call, boolean ok, String motivo) {
        JSObject r = new JSObject();
        r.put("ok", ok);
        if (motivo != null) r.put("motivo", motivo);
        call.resolve(r);
    }
}
