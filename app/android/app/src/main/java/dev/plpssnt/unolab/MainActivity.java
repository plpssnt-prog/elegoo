package dev.plpssnt.unolab;

import android.content.Intent;
import android.hardware.usb.UsbManager;
import android.os.Bundle;

import com.getcapacitor.BridgeActivity;
import com.getcapacitor.PluginHandle;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        // collegamento USB nativo con la UNO (al posto di WebUSB, che nella WebView non c'è)
        registerPlugin(UnoSerialPlugin.class);
        super.onCreate(savedInstanceState);
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        // app già aperta e scheda appena collegata: avvisa la pagina, che si ricollega da sola
        if (intent != null && UsbManager.ACTION_USB_DEVICE_ATTACHED.equals(intent.getAction()) && bridge != null) {
            PluginHandle h = bridge.getPlugin("UnoSerial");
            if (h != null && h.getInstance() instanceof UnoSerialPlugin) ((UnoSerialPlugin) h.getInstance()).schedaAttaccata();
        }
    }
}
