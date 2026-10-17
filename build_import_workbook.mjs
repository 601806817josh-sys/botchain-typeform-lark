import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = process.cwd();
const outputDir = path.join(root, "outputs", "01a02388-b463-7d42-a981-2fc896aa0e5b");
const outputPath = path.join(outputDir, "BOT-Chain-Lark-Base-Import.xlsx");

const definitions = [
  ["总申请表", "master-fields.json", "#1F4E78"],
  ["生态扶持奖励", "ecosystem-fields.json", "#0F766E"],
  ["Gas返佣", "gas-fields.json", "#B45309"],
  ["活动合作", "event-fields.json", "#7C3AED"],
  ["孵化加速", "incubation-fields.json", "#B91C1C"],
];

const workbook = Workbook.create();

for (const [sheetName, fileName, color] of definitions) {
  const schema = JSON.parse(
    await fs.readFile(path.join(root, "schemas", fileName), "utf8"),
  );
  const headers = schema.map((field) => field.name);
  const sheet = workbook.worksheets.add(sheetName);
  sheet.showGridLines = false;
  sheet.tabColor = color;
  sheet.getRangeByIndexes(0, 0, 1, headers.length).values = [headers];
  const header = sheet.getRangeByIndexes(0, 0, 1, headers.length);
  header.format = {
    fill: color,
    font: { name: "Arial", size: 10, bold: true, color: "#FFFFFF" },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "all", style: "thin", color: "#D9E2F3" },
  };
  header.format.rowHeight = 34;
  header.format.autofitColumns();
  for (let i = 0; i < headers.length; i += 1) {
    const col = sheet.getRangeByIndexes(0, i, 2, 1);
    const currentWidth = col.format.columnWidth;
    if (!currentWidth || currentWidth > 28) col.format.columnWidth = 24;
  }
  sheet.freezePanes.freezeRows(1);
}

workbook.recalculate();

const inspection = await workbook.inspect({
  kind: "sheet,region",
  maxChars: 8000,
  tableMaxRows: 3,
  tableMaxCols: 40,
});
console.log(inspection.ndjson);

await fs.mkdir(outputDir, { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(JSON.stringify({ outputPath, sheets: definitions.map(([name]) => name) }));
