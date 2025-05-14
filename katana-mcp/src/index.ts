import { createToolServer, z, ToolRunContext } from "@modelcontextprotocol/sdk";
import { spawn } from "child_process";

const KATANA_BIN = "katana";                       // assumes binary in $PATH

// ---------- Schema ----------
const schema = z.object({
  args: z
    .string()
    .describe(
      "Command-line flags to forward to Katana (e.g. '-u https://example.com -jc'). " +
      "Leave empty for a default quick crawl."
    )
});

// ---------- Helper ----------
async function runKatana(cliArgs: string): Promise<Buffer> {
  const argList =
    cliArgs.trim().length > 0 ? cliArgs.trim().split(/\s+/) : ["-u", "https://example.com"];
  return new Promise((resolve, reject) => {
    const proc = spawn(KATANA_BIN, argList, { stdio: ["ignore", "pipe", "inherit"] });
    const chunks: Buffer[] = [];
    proc.stdout.on("data", (c) => chunks.push(c));
    proc.once("error", reject);
    proc.once("close", (code) =>
      code === 0
        ? resolve(Buffer.concat(chunks))
        : reject(new Error(`katana exited with code ${code}`))
    );
  });
}

// ---------- MCP server ----------
createToolServer({
  name: "katana",
  description: "Fast CLI web crawler by ProjectDiscovery.",
  schema,

  async run({ input, logger }: ToolRunContext<typeof schema>) {
    logger.info(`Running Katana with: ${input.args || "(default args)"}`);
    const output = await runKatana(input.args);
    return { contentType: "text/plain", data: output };
  }
});
