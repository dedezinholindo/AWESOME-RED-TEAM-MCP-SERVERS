import { createToolServer, z } from "@modelcontextprotocol/sdk";
import { spawn } from "child_process";
import path from "path";

const KATANA_BIN = "katana";                 // assumes in $PATH

/** Tool signature passed to Claude */
const schema = z.object({
  args: z
    .string()
    .describe(
      "Command-line flags to forward to katana, e.g. '-u https://example.com -jc -o output.jsonl'. " +
      "Leave blank for default fast crawl."
    )
});

/** Spawn katana and stream JSONL/stdout back to the LLM. */
async function runKatana(cliArgs: string) {
  return new Promise<Buffer>((resolve, reject) => {
    const args = cliArgs.trim().length ? cliArgs.trim().split(/\s+/) : ["-u", "https://example.com"];
    const proc = spawn(KATANA_BIN, args, { stdio: ["ignore", "pipe", "inherit"] });

    let buf = Buffer.alloc(0);
    proc.stdout.on("data", (chunk) => (buf = Buffer.concat([buf, chunk])));
    proc.on("error", reject);
    proc.on("close", (code) => {
      if (code === 0) resolve(buf);
      else reject(new Error(`katana exited with code ${code}`));
    });
  });
}

/** Register as an MCP tool server */
createToolServer({
  name: "katana",
  description: "Fast CLI web crawler by ProjectDiscovery.",
  schema,
  run: async ({ input, logger }) => {
    logger.info(`Running katana with: ${input.args}`);
    const output = await runKatana(input.args);
    return { contentType: "text/plain", data: output };
  }
});
