import Vue from "vue";
import App from "./App";

import store from "./store";
import "./style.less";

new Vue({
	el: "#app",
	store,
	render: (h: any) => h(App)
});
