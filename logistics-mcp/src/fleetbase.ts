
import axios from 'axios';

const FLEETBASE_URL = process.env.FLEETBASE_URL || 'http://localhost:3000';

export async function createDriver(name: string, status: string = 'active') {
    try {
        const response = await axios.post(`${FLEETBASE_URL}/drivers`, { name, status });
        return response.data;
    } catch (error: any) {
        throw new Error(`Failed to create driver: ${error.message}`);
    }
}

export async function createOrder(payload: any) {
    try {
        const response = await axios.post(`${FLEETBASE_URL}/orders`, payload);
        return response.data;
    } catch (error: any) {
        throw new Error(`Failed to create order: ${error.message}`);
    }
}

export async function assignDriver(orderId: string, driverId: string) {
    try {
        const response = await axios.post(`${FLEETBASE_URL}/orders/${orderId}/dispatch`, { driver_id: driverId });
        return response.data;
    } catch (error: any) {
        throw new Error(`Failed to assign driver: ${error.message}`);
    }
}

export async function listDrivers() {
    try {
        const response = await axios.get(`${FLEETBASE_URL}/drivers`);
        return response.data;
    } catch (error: any) {
        throw new Error(`Failed to list drivers: ${error.message}`);
    }
}
