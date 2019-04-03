<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";
import generateTicketsMain from "./ticketsgenerate";
import axios from "axios";
import { get as getCookie } from "js-cookie";


const axiosInstance = axios.create({
    baseURL: '/grade/ticket/',
    headers: {
        'X-CSRFToken': getCookie('csrftoken'),
    },
});

@Component
export default class App extends Vue {
  ticketGenerationFinished: boolean = false;
  tickets: string = '';

  async generateTicketsOnClick() {
    this.tickets = await generateTicketsMain();
    this.ticketGenerationFinished = true;
  }

  copyTickets() {
    let ticketsToCopy = document.querySelector('#tickets') as HTMLInputElement;
    ticketsToCopy.select();
    document.execCommand('copy');
  }
}
</script>

<template>
  <div style="text-align: center">
    <button
      id="tickets_generate_button"
      class="btn"
      v-if="!ticketGenerationFinished"
      v-on:click="generateTicketsOnClick"
    >Pobierz klucze</button>
    <div v-if="ticketGenerationFinished">
      <div id="grade-tickets-save-form">
        <h3>Pomyślnie wygenerowano klucze.</h3>
        <h3>
          Zapisz je w bezpiecznym miejscu -
          <strong>nie ma powrotu do tego ekranu</strong>.
        </h3>
        <br>
        <div style="text-align: center">
          <button id="copy-keys" class="btn btn-default" v-on:click="copyTickets">Skopiuj</button>
        </div>
        <br>
        <textarea id="tickets" name="tickets" v-model="tickets" style="width:1000px; height:400px"></textarea>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
</style>
