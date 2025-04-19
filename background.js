function sendToLocalApp(url) {
  const port = browser.runtime.connectNative("ytdlp.firefox.extension.app");
  port.postMessage({ "url": url });
  port.onMessage.addListener((response) => {
    console.log("Got response:", response);
  });

  port.onDisconnect.addListener(() => {
    if (browser.runtime.lastError) {
      console.error("Disconnect error:", browser.runtime.lastError.message);
    }
  });
}

browser.browserAction.onClicked.addListener((tab) => {
  const url = tab.url;
  sendToLocalApp(url);
});
