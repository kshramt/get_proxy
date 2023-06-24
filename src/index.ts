import * as Express from "express";
import { chromium } from "playwright-extra";
import * as Zlib from "zlib";
import Peps from "puppeteer-extra-plugin-stealth";

chromium.use(Peps());
const browser = chromium.launch({ headless: true });
const ctx = browser.then((browser) =>
  browser.newContext({ locale: process.env.BROWSER_LOCALE || "en-US" }),
);

const app = Express.default();
const port = process.env.PORT || 8080;

const DEFAULT_SLEEP_MSEC = 2000;

const sleep = (msec: number) => {
  return new Promise((resolve) => setTimeout(resolve, msec));
};

app.get("/", async (req, res) => {
  const uri = req.query.uri;
  if (typeof uri !== "string") {
    res.sendStatus(400);
    return;
  }
  let mean_sleep_msec = DEFAULT_SLEEP_MSEC;
  const sleep_query = req.query.sleep;
  if (typeof sleep_query === "string") {
    mean_sleep_msec = parseInt(sleep_query, 10);
    if (isNaN(mean_sleep_msec)) {
      mean_sleep_msec = DEFAULT_SLEEP_MSEC;
    }
  }
  const sleep_msec = Math.random() * mean_sleep_msec;
  await sleep(sleep_msec);
  const result = await getContent(uri);
  const b = Zlib.gzipSync(JSON.stringify(result));
  res.setHeader("Content-Type", "application/octet-stream");
  res.send(b);
});

app.get("/admin/health", async (req, res) => {
  res.sendStatus(204);
});

app.listen(port, () => {
  console.log(`Listening on port ${port}`);
});

const getContent = async (uri: string) => {
  const page = await (await ctx).newPage();
  try {
    await page.goto(uri);
    const content = await page.content();
    return {
      source: content,
      error: null,
    };
  } catch (err: unknown) {
    if (!err?.toString) {
      return {
        source: null,
        error: "!err?.toString",
      };
    }
    return {
      source: null,
      error: err.toString(),
    };
  } finally {
    await page.close();
  }
};
