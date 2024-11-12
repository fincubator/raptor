import { createApp } from 'vue';
import App from './App.vue';
import i18n from './i18n';
import './assets/styles.css';
import './assets/components.css';
import './assets/V01.css';
import './assets/index.css';

const app = createApp(App);
app.use(i18n);
app.mount('#app');
