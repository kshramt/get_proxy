import * as Express from "express";
import { chromium } from "playwright-extra";
import * as Zlib from "zlib";
import Peps from "puppeteer-extra-plugin-stealth";

chromium.use(Peps());
const browser = chromium.launch({ headless: true });

const app = Express.default();
const port = process.env.PORT || 8080;

app.get("/", async (req, res) => {
  const { uri } = req.query;
  if (typeof uri !== "string") {
    res.sendStatus(400);
    return;
  }
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
  const ctx = await (await browser).newContext();
  try {
    const page = await ctx.newPage();
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
    await ctx.close();
  }
};
