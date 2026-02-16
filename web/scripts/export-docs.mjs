import { cpSync, existsSync, mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const outDir = resolve(process.cwd(), "out");
const docsDir = resolve(process.cwd(), "..", "docs");

if (!existsSync(outDir)) {
  throw new Error("web/out not found. Run next build first.");
}

mkdirSync(docsDir, { recursive: true });
cpSync(outDir, docsDir, { recursive: true });
writeFileSync(resolve(docsDir, ".nojekyll"), "");
console.log(`Copied static site to ${docsDir}`);
