document.getElementById("download-video-btn").addEventListener("click", () => {
  console.log("Menu Item 1 clicked");
  sendMessage({ action: "video" });
});

document
  .getElementById("download-audio-only-btn")
  .addEventListener("click", () => {
    console.log("Menu Item 2 clicked");
    sendMessage({ action: "audio-only" });
  });

async function sendMessage(message) {
  tabs = await browser.tabs.query({ active: true, currentWindow: true });
  if (tabs.length == 0) {
    return;
  }
  message.url = tabs[0].url;
  browser.runtime.sendMessage(message, (response) => {
    console.log("response received: ", response);
  });
}
