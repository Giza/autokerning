import ndarray from "ndarray";
import { Glyph } from "./glyph.js";
import { createCanvas } from "canvas";
import { logger } from "./log.js";

let debugCount = 0;

/**
 * Compute pixel overlap using composition logic from Python version
 *
 * Intersection rectangle layout:
 * - Right glyph at x ∈ [0, right.width)
 * - Left glyph at x ∈ [lOffset, lOffset + left.width)
 * - Only pixels in both ranges contribute to overlap
 */
export function overlap(left: Glyph, right: Glyph, kern: number): number {
  const height = left.height;

  // Calculate offset where left glyph is positioned relative to right
  const lOffset = -(left.advance + left.bboxOffsetX) + right.bboxOffsetX - kern;

  // Find intersection range in x-dimension
  const xStart = Math.max(0, lOffset);
  const xEnd = Math.min(right.width, lOffset + left.width);
  const width = Math.max(0, xEnd - xStart);

  if (debugCount < 3 && width > 0) {
    logger.debug(
      `[OVERLAP] pair=${left.char}${right.char}, kern=${kern
        .toString()
        .padStart(4)}, lOffset=${lOffset
          .toFixed(2)
          .padStart(8)}, [${xStart.toFixed(0)}, ${xEnd.toFixed(0)}) width=${width
            .toFixed(0)
            .padStart(4)}`
    );
  }

  if (width <= 0) {
    return 0;
  }

  // Compute intersection by multiplying pixel values
  let sum = 0;

  // Use direct typed-array access to avoid ndarray.get overhead inside tight loops
  const rData = (right.bitmap as any).data as Float32Array | Float64Array;
  const lData = (left.bitmap as any).data as Float32Array | Float64Array;
  const rW = right.width;
  const lW = left.width;
  const rH = right.height;
  const lH = left.height;

  // Pre-calculate valid Y intersection to avoid checking y < lH and y < rH later
  const yEnd = Math.min(height, lH, rH);

  // x and y must be precise integers representing pixel coordinates
  // The intersection of valid pixels in both glyphs:
  // Right glyph validity: 0 <= x < rW
  // Left glyph validity:  0 <= (x - lOffset) < lW  =>  lOffset <= x < lOffset + lW
  // Therefore, valid global x coordinates must satisfy BOTH:
  const finalStartX = Math.ceil(Math.max(0, lOffset));
  const finalEndX = Math.ceil(Math.min(rW, lOffset + lW));

  if (finalStartX >= finalEndX || yEnd <= 0) {
    if (debugCount < 3 && width > 0) {
      logger.error(`         -> overlap=    0.00`);
      debugCount++;
    }
    return 0;
  }

  // Pre-calculate how local left indices map to global X inside the loop
  // lx = x - lOffset
  // Let l_idx = floor(x - lOffset)
  // Since x is integer, we can pull out the offset part
  // Let shift = Math.floor(-lOffset) or similar. 
  // Wait, if lOffset is float, Math.floor(x - lOffset) = x + Math.floor(-lOffset)
  const lShift = Math.floor(-lOffset);

  // Use direct typed-array access

  for (let y = 0; y < yEnd; y++) {
    const rRowOff = y * rW;
    const lRowOff = y * lW;

    // Everything in this loop is guaranteed valid
    for (let x = finalStartX; x < finalEndX; x++) {
      const rVal = rData[rRowOff + x];
      // For left index:
      // lx = x - lOffset
      // li = Math.floor(lx) = x + Math.floor(-lOffset)
      const li = x + lShift;
      const lVal = lData[lRowOff + li];

      sum += lVal * lVal * rVal * rVal;
    }
  }

  if (debugCount < 3 && width > 0) {
    logger.error(`         -> overlap=${sum.toFixed(2).padStart(8)}`);
    debugCount++;
  }

  return sum;
}

// Export function to set bbox offset (needed during glyph creation)
export function setGlyphBboxOffset(glyph: Glyph, offsetX: number): void {
  (glyph as any).bboxOffsetX = offsetX;
}
