import { getPrivateKey, getWalletAddress } from "./config.js";

type ToolHandler = (args: unknown) => Promise<string>;

const get_wallet_info: ToolHandler = async () => {
  try {
    const address = getWalletAddress();
    
    return JSON.stringify({
      address,
      source: "MOLTX_PRIVATE_KEY environment variable",
      configPath: "~/.moltx/config.json",
    });
  } catch (error) {
    return JSON.stringify({
      error: (error as Error).message,
      hint: "Make sure MOLTX_PRIVATE_KEY is set in your environment",
    });
  }
};

export const walletTools: Record<string, ToolHandler> = {
  get_wallet_info,
};
