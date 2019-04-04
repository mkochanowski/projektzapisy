<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";
import generateTicketsMain from "./ticketsgenerate";
import axios from "axios";
import { get as getCookie } from "js-cookie";


@Component
export default class TicketsGenerator extends Vue {
  ticketGenerationFinished: boolean = false;
  tickets: string = "";
  loading: boolean = false;

  async generateTicketsOnClick() {
    this.loading = true;
    this.tickets = await generateTicketsMain();
    this.loading = false;
    this.ticketGenerationFinished = true;
  }

  copyTickets() {
    let ticketsTextArea = this.$refs["tickets-textarea"] as HTMLInputElement;
    ticketsTextArea.select();
    document.execCommand("copy");
  }
}
</script>

<template>
  <div class="text-center">
    <button
      id="tickets_generate_button"
      class="btn btn-primary"
      v-if="!ticketGenerationFinished"
      @click="generateTicketsOnClick"
    ><span v-if="loading" class="spinner-border spinner-border-sm"></span>Pobierz klucze</button>
    <div v-if="ticketGenerationFinished">
      <div id="grade-tickets-save-form">
        <h3>Pomyślnie wygenerowano klucze.</h3>
        <h3>
          Zapisz je w bezpiecznym miejscu -
          <strong>nie ma powrotu do tego ekranu</strong>.
        </h3>
        <br>
        <div class="text-center">
          <button id="copy-keys" class="btn btn-primary" @click="copyTickets">
            Skopiuj
          </button>
        </div>
        <br>
        <textarea
          ref="tickets-textarea"
          id="tickets"
          name="tickets"
          v-model="tickets"
          style="width:1000px; height:400px"
        ></textarea>
      </div>
    </div>
  </div>
</template>
