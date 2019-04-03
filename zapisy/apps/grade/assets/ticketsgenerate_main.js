import Vue from 'vue'
import App from './App.vue'

Vue.config.productionTip = false;

window.onload = function() {
    new Vue({
        el: '#app',
        render: h => h(App)
    });
};
