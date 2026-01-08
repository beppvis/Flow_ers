
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
    CallToolRequestSchema,
    ListToolsRequestSchema,
    ListResourcesRequestSchema,
    ReadResourceRequestSchema
} from "@modelcontextprotocol/sdk/types.js";
import dotenv from 'dotenv';
import * as fleetbase from './fleetbase.js';
import * as frappe from './frappe.js';

dotenv.config();

const server = new Server(
    {
        name: "logistics-mcp",
        version: "1.0.0",
    },
    {
        capabilities: {
            resources: {},
            tools: {},
        },
    }
);

// --- Resources ---
server.setRequestHandler(ListResourcesRequestSchema, async () => {
    return {
        resources: [
            {
                uri: "erpnext://all/drivers_summary",
                name: "Drivers Summary (Fleetbase + ERPNext)",
                mimeType: "application/json",
            }
        ]
    };
});

server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
    const uri = request.params.uri;
    if (uri === "erpnext://all/drivers_summary") {
        const drivers = await fleetbase.listDrivers();
        return {
            contents: [{
                uri,
                mimeType: "application/json",
                text: JSON.stringify(drivers, null, 2)
            }]
        };
    }
    throw new Error("Resource not found");
});

// --- Tools ---
server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
        tools: [
            {
                name: "create_erpnext_receipt",
                description: "Create a Receipt/Sales Order in ERPNext (Frappe).",
                inputSchema: {
                    type: "object",
                    properties: {
                        customer: { type: "string" },
                        items: {
                            type: "array",
                            items: {
                                type: "object",
                                properties: {
                                    item_code: { type: "string" },
                                    qty: { type: "number" }
                                }
                            }
                        }
                    },
                    required: ["customer", "items"]
                },
            },
            {
                name: "create_fleetbase_order",
                description: "Create a generic order in Fleetbase for logistics.",
                inputSchema: {
                    type: "object",
                    properties: {
                        recipient: { type: "string" },
                        address: { type: "string" },
                        details: { type: "string" }
                    },
                    required: ["recipient", "address"]
                },
            },
            {
                name: "find_and_assign_driver",
                description: "Find an available driver in Fleetbase and assign them to an order.",
                inputSchema: {
                    type: "object",
                    properties: {
                        order_id: { type: "string" }
                    },
                    required: ["order_id"]
                },
            },
            {
                name: "get_drivers",
                description: "List all drivers from Fleetbase.",
                inputSchema: {
                    type: "object",
                    properties: {}
                },
            }
        ],
    };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    try {
        if (name === "create_erpnext_receipt") {
            if (!args) throw new Error("Missing arguments");
            // Map to Frappe 'Sales Order' or 'Delivery Note'
            const result = await frappe.createDocument("Sales Order", {
                customer: args.customer,
                items: args.items,
                transaction_date: new Date().toISOString().split('T')[0]
            });
            return {
                content: [{ type: "text", text: JSON.stringify(result) }]
            };
        }

        if (name === "create_fleetbase_order") {
            if (!args) throw new Error("Missing arguments");
            const result = await fleetbase.createOrder(args);
            return {
                content: [{ type: "text", text: JSON.stringify(result) }]
            };
        }

        if (name === "get_drivers") {
            const result = await fleetbase.listDrivers();
            return {
                content: [{ type: "text", text: JSON.stringify(result) }]
            };
        }

        if (name === "find_and_assign_driver") {
            if (!args) throw new Error("Missing arguments");
            const orderId = String(args.order_id);
            const drivers = await fleetbase.listDrivers();
            // Simple logic: find first active driver
            const driver = drivers.find((d: any) => d.status === 'active');

            if (!driver) {
                return {
                    content: [{ type: "text", text: "No active drivers found." }],
                    isError: true
                };
            }

            const assignment = await fleetbase.assignDriver(orderId, driver.id);
            return {
                content: [{ type: "text", text: `Assigned driver ${driver.name} to order ${orderId}. Details: ${JSON.stringify(assignment)}` }]
            };
        }

        throw new Error(`Unknown tool: ${name}`);
    } catch (error: any) {
        return {
            content: [{ type: "text", text: `Error: ${error.message}` }],
            isError: true,
        };
    }
});

const transport = new StdioServerTransport();
await server.connect(transport);
