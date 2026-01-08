
import axios from 'axios';

const ERPNEXT_URL = process.env.ERPNEXT_URL || 'http://localhost:8000';
// Using basic auth or token based on simple params for now as per reference
const ERPNEXT_API_KEY = process.env.ERPNEXT_API_KEY;
const ERPNEXT_API_SECRET = process.env.ERPNEXT_API_SECRET;

function getHeaders() {
    if (ERPNEXT_API_KEY && ERPNEXT_API_SECRET) {
        return {
            'Authorization': `token ${ERPNEXT_API_KEY}:${ERPNEXT_API_SECRET}`,
            'Content-Type': 'application/json'
        };
    }
    return { 'Content-Type': 'application/json' };
}

export async function createDocument(doctype: string, data: any) {
    try {
        // Determine if we need to authenticate (mock flow might assume admin)
        const response = await axios.post(
            `${ERPNEXT_URL}/api/resource/${doctype}`,
            data,
            { headers: getHeaders() }
        );
        return response.data;
    } catch (error: any) {
        // If we are in a dev environment without a real ERPNext, we might want to mock success
        // But for now, let's allow it to fail or mock if connection refused
        if (error.code === 'ECONNREFUSED') {
            console.warn("ERPNext unreachable, MOCKING success for hackathon demo purposes.");
            return {
                data: {
                    name: `MOCK-${doctype}-${Date.now()}`,
                    ...data
                }
            };
        }
        throw new Error(`Failed to create ${doctype}: ${error.message}`);
    }
}

export async function getDocument(doctype: string, name: string) {
    try {
        const response = await axios.get(
            `${ERPNEXT_URL}/api/resource/${doctype}/${name}`,
            { headers: getHeaders() }
        );
        return response.data;
    } catch (error: any) {
        if (error.code === 'ECONNREFUSED') {
            return { data: { name, doctype, status: 'MOCK_DATA' } };
        }
        throw new Error(`Failed to get ${doctype} ${name}: ${error.message}`);
    }
}
