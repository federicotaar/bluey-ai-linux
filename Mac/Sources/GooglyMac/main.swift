// Entry point of the Mac app: installs AppDelegate and runs as a menu-bar
// accessory (no Dock icon).

import AppKit

MainActor.assumeIsolated {
    let app = NSApplication.shared
    let delegate = AppDelegate()
    app.delegate = delegate
    app.setActivationPolicy(.accessory)  // menu bar only, no Dock icon
    app.run()
}
