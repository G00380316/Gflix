# -*- coding: utf-8 -*-
import xbmc, xbmcgui


def open_channel_guide():
    target = (xbmc.getLocalizedString(19686) or "").strip()
    if not target:
        return
    home = xbmcgui.Window(10000)
    home.setProperty("altus.pvr.hiding_ctx", "true")
    try:
        monitor = xbmc.Monitor()
        xbmc.executebuiltin("Action(ContextMenu)")
        for _ in range(40):
            if xbmc.getCondVisibility("Window.IsVisible(contextmenu)"):
                break
            if monitor.waitForAbort(0.02):
                return
        else:
            return
        for _ in range(60):
            label = (xbmc.getInfoLabel("System.CurrentControl") or "").strip()
            if label and label == target:
                xbmc.executebuiltin("Action(Select)")
                return
            xbmc.executebuiltin("Action(Up)")
            for _ in range(20):
                if monitor.waitForAbort(0.005):
                    return
                if (xbmc.getInfoLabel("System.CurrentControl") or "").strip() != label:
                    break
        xbmc.executebuiltin("Action(Close)")
    finally:
        xbmc.sleep(300)
        home.clearProperty("altus.pvr.hiding_ctx")
