import { generateKerningTable } from './dist/index.js';

async function main() {
    console.log("Testing Programmatic API...");
    const { kerningTable } = await generateKerningTable('./FZFWZhuZiAYuanS-D.ttf', {
        pairs: ['АБ', 'АФ', 'Та', 'Фк'],
        writeFile: false
    });
    console.log("API Result:", kerningTable);
}

main().catch(console.error);
