// Sends the text to our own server (same website), so no API key is ever in the browser.
const form = document.getElementById("form");
const text = document.getElementById("text");
const out = document.getElementById("out");
const go = document.getElementById("go");
const count = document.getElementById("count");

const updateCount = () => (count.textContent = `${text.value.length} / 1000`);
text.addEventListener("input", updateCount);
updateCount();

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  go.disabled = true;
  out.hidden = false;
  out.textContent = "Thinking…";
  try {
    const res = await fetch("/api/mood", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text.value }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Please check your text.");
    const positive = data.label === "POSITIVE";
    out.innerHTML = "";
    const big = document.createElement("div");
    big.className = "big " + (positive ? "pos" : "neg");
    big.textContent = (positive ? "😊 " : "😟 ") + data.label;
    const info = document.createElement("div");
    info.className = "muted";
    info.textContent = `Confidence ${(data.confidence * 100).toFixed(1)}% · answered in ${data.milliseconds} ms`;
    out.append(big, info);
  } catch (err) {
    out.textContent = "Something went wrong: " + err.message;
  } finally {
    go.disabled = false;
  }
});
