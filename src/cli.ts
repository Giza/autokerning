#!/usr/bin/env node
import { Command } from "commander";
import * as opentype from "opentype.js";
import { renderGlyph } from "./glyph.js";
import { kernPair } from "./kernPair.js";
import { gaussianBlur } from "./blur.js";
import * as fs from "fs";

import { generateKerningTable, findS } from "./generateKerningTable.js";

const program = new Command();

program
  .name("autokerning")
  .description("Auto-compute kerning values for fonts")
  .argument("<fontfile>", "Path to font file (.ttf/.otf)")
  .argument("[pairs...]")
  .option("-s, --size <n>", "Font size (default 100)", "100")
  .option(
    "-o, --output <file>",
    "Generate kerning JSON file like generate-kerning"
  )
  .option(
    "--pairs <list>",
    "Comma-separated list of pairs to analyze for JSON output"
  )
  .parse(process.argv);

const fontfile = program.args[0];
let pairs = program.args.slice(1);
const outputFile = program.opts().output;
const pairsString = program.opts().pairs;

// Convert comma-separated pairs string or read from text file
let pairsList: string[] | undefined;
if (pairsString) {
  if (pairsString.endsWith(".txt")) {
    try {
      const fileContent = fs.readFileSync(pairsString, "utf-8");
      pairsList = fileContent.split(",").map((p: string) => p.trim());
    } catch (e) {
      console.error(`Failed to read pairs file: ${e}`);
      process.exit(1);
    }
  } else {
    pairsList = pairsString.split(",").map((p: string) => p.trim());
  }
}
import { COMMON_PAIRS } from "./commonPairs.js";

// use findS exported from generateKerningTable (calibrated adaptive kernel)

(async () => {
  if (outputFile) {
    const { outputPath, kerningTable } = await generateKerningTable(fontfile, {
      outputfile: outputFile,
      pairs: pairsList || (pairs.length > 0 ? pairs : undefined),
      writeFile: true,
    });
    console.log(`Kerning table saved to: ${outputPath}`);
    console.log(`Total pairs: ${Object.keys(kerningTable).length}`);
    return;
  }

  // If no pairs provided, use default common pairs
  if (!pairs.length) {
    pairs = COMMON_PAIRS;
  }

  const font = await opentype.load(fontfile);
  // Calibrate overlap thresholds (findS returns [minS, maxS, kernelWidth])
  const [minS, maxS, kernelWidth] = findS(font);
  for (const pair of pairs) {
    if (pair.length !== 2) continue;
    const [lch, rch] = pair;
    const left = renderGlyph(font, lch);
    const right = renderGlyph(font, rch);
    const blurredLeft = { ...left, bitmap: gaussianBlur(left.bitmap, undefined, kernelWidth) };
    const blurredRight = { ...right, bitmap: gaussianBlur(right.bitmap, undefined, kernelWidth) };
    const kern = kernPair(blurredLeft, blurredRight, minS, maxS, kernelWidth);
    console.log(`${pair}: suggested kerning ${kern.toFixed(2)} (px)`);
  }
})();
