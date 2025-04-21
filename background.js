function sendToLocalApp(message) {
  const port = browser.runtime.connectNative("ytdlp.firefox.extension.app");
  port.postMessage(message);
  port.onMessage.addListener((response) => {
    console.log("Got response:", response);
    port.disconnect();
  });

  port.onDisconnect.addListener(() => {
    if (browser.runtime.lastError) {
      console.error("Disconnect error:", browser.runtime.lastError.message);
    }
  });
}

browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log("message: ", message);
  sendToLocalApp(message);
  sendResponse({ status: "ok" });
  return false;
});
