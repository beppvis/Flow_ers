
import { GoogleGenerativeAI } from "@google/generative-ai";
import { spawn } from "child_process";
import dotenv from "dotenv";
import * as readline from "readline";

dotenv.config();

const apiKey = process.env.GEMINI_API_KEY;
if (!apiKey) {
    console.error("GEMINI_API_KEY is not set in .env");
    process.exit(1);
}

const genAI = new GoogleGenerativeAI(apiKey);

// --- MCP Client Helper ---
// In a real scenario, use a proper MCP Client SDK. Here we spawn the server and parse stdio.
// Actually, using the MCP SDK's Client class is better if we can, but connecting it to stdio 
// of a child process manually in a simple script is complex. 
// FOR SIMPLICITY: We will MOCK the Agent's tool calling behavior or use a simplified interaction.
// The user wants "The agent receive a text based command... then proceeds to assign...".

// To truly demonstrate MCP, we should spin up the server and interact.
// However, implementing a full MCP Client in this script is heavy.
// Let's use the Gemini Function Calling API definitions matching our MCP tools,
// and when Gemini calls a function, we invoke the Local MCP server logic directly (or dispatch to it).

// BUT, since we are in the SAME project, maybe we can just import the functions directly?
// No, the request is to build an MCP *server*.
// So this client acts as the "Host" connecting Gemini -> MCP Server.

// Let's define the tools for Gemini manually that match our MCP tools.
const tools = [
    {
        name: "create_erpnext_receipt",
        description: "Create a Receipt/Sales Order in ERPNext.",
        parameters: {
            type: "OBJECT",
            properties: {
                customer: { type: "STRING" },
                items: {
                    type: "ARRAY",
                    items: {
                        type: "OBJECT",
                        properties: {
                            item_code: { type: "STRING" },
                            qty: { type: "NUMBER" }
                        }
                    }
                }
            },
            required: ["customer", "items"]
        }
    },
    {
        name: "create_fleetbase_order",
        description: "Create a generic order in Fleetbase.",
        parameters: {
            type: "OBJECT",
            properties: {
                recipient: { type: "STRING" },
                address: { type: "STRING" },
                details: { type: "STRING" }
            },
            required: ["recipient", "address"]
        }
    },
    {
        name: "find_and_assign_driver",
        description: "Find a driver and assign to an order.",
        parameters: {
            type: "OBJECT",
            properties: {
                order_id: { type: "STRING" }
            },
            required: ["order_id"]
        }
    }
];

const model = genAI.getGenerativeModel({
    model: "gemini-2.0-flash-exp", // Or gemini-pro
    tools: [{ functionDeclarations: tools as any }]
});

// We need a way to execute the tool on the MCP server.
// For this demo script, to keep it simple and showing it works:
// We will simple import the functions from our source files (bypassing the stdio transport for the DEMO client only).
// In a real production "MCP Client" (like Claude Desktop), it speaks JSON-RPC over Stdio.
// Emulating that here requires valid JSON-RPC wrapping.

import * as fleetbase from './src/fleetbase.js';
import * as frappe from './src/frappe.js';

async function executeTool(name: string, args: any) {
    console.log(`[Client] Agent executing tool: ${name} with args:`, args);

    if (name === "create_erpnext_receipt") {
        // Map args
        return await frappe.createDocument("Sales Order", {
            customer: args.customer,
            items: args.items,
            transaction_date: new Date().toISOString().split('T')[0]
        });
    }
    if (name === "create_fleetbase_order") {
        return await fleetbase.createOrder(args);
    }
    if (name === "find_and_assign_driver") {
        const orderId = String(args.order_id);
        const drivers = await fleetbase.listDrivers();
        const driver = drivers.find((d: any) => d.status === 'active');
        if (!driver) throw new Error("No drivers");
        return await fleetbase.assignDriver(orderId, driver.id);
    }
    return { error: "Unknown tool" };
}

async function run() {
    const chat = model.startChat();
    const userPrompt = "Ship 10 units of eggs to MrX. Create a receipt in ERPNext (Customer: MrX) and then create an order in Fleetbase to 123 Main St. finally Assign a driver to the order.";

    console.log(`[User] ${userPrompt}`);

    let result = await chat.sendMessage(userPrompt);
    let response = result.response;
    let functionCalls = response.functionCalls();
    let run = false

    console.log(`[Agent] Initial thought received.`);

    while (functionCalls && functionCalls.length > 0 && !run) {
        for (const call of functionCalls) {
            console.log(`[Agent] Calling function: ${call.name}`);
            try {
                const toolResult = await executeTool(call.name, call.args);
                console.log(`[Tool Output]`, toolResult);

                // Pass result back to model
                result = await chat.sendMessage([{
                    functionResponse: {
                        name: call.name,
                        response: { content: toolResult }
                    }
                }]);
            } catch (e: any) {
                console.error(`[Tool Error]`, e.message);
                // Continue or fail
            }
        }
        response = result.response;
        functionCalls = response.functionCalls();
        break;
    }

    console.log(`[Agent] Final Response: ${response.text()}`);
}

// Check if we can run (mocks might be needed for imports to work if TS isn't compiled)
// This script is meant to be run with ts-node
run().catch(console.error);
