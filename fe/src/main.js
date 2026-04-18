import { createApp } from 'vue';
import { createPinia } from 'pinia';
import router from './router';
import { createI18nInstance } from './i18n';
import App from './App.vue';
import './style.css';

const i18n = createI18nInstance();
const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.use(i18n);
app.mount('#app');
