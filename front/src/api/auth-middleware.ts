import { useAuthStore } from '@/stores/auth-store';
import { type Middleware } from 'openapi-fetch';

export const authMiddleware: Middleware = {
    async onRequest({ request }) {
        // set "foo" header
        // request.headers.set("Authorization", "bar");

        const authStore = useAuthStore();
        if (authStore.token) {
            request.headers.set("Authorization", `Bearer ${authStore.token}`);
        }

        return request;
    },
    async onResponse({ response }) {
        // const { body, ...resOptions } = response;
        // change status of response
        // return new Response(body, { ...resOptions, status: 200 });

        if (response.status == 401) {
            const authStore = useAuthStore();
            authStore.logout();
        }

        return response;
    },
    async onError({ error }) {
        // wrap errors thrown by fetch
        return new Error('Oops, fetch failed ' + error);
    },
};
