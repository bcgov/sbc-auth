<template>
  <v-dialog v-model="isDialogOpen" max-width="1140">
    <v-card class="d-flex">
      <!-- Left Panel -->
      <div class="col-4 p-5">
        <p>AUTHENTICATION OPTIONS</p>
        <h2>
          <v-icon large color="primary" class="mr-4">mdi-account-card-details-outline</v-icon><span>BC Services Card</span>
        </h2>
        <div class="my-3">
          <ul>
            <li>The BC Services Card enables safe and secure access to government digital services. BC residents may have the combined Driver's License or a stand-alone Services Card.</li>
            <li>Registries only ever accesses your name and surname. We never access health, driving, or any other personal information.</li>
            <li>There are two options for logging in with the BC Services Card. Review the diagrams on this screen for information on how they work.</li>
          </ul>
        </div>
        <div class="account-type__buttons">
          <v-btn
            large
            depressed
            block
            color="primary"
            class="font-weight-bold mb-3"
            @click="select()"
          >
            SELECT
          </v-btn>
          <v-btn
            large
            depressed
            block
            color="primary"
            class="font-weight-bold"
            outlined
            @click="close()"
          >
            More Options
          </v-btn>
        </div>
      </div>

      <v-divider vertical />

      <!-- Right Panel -->
      <div class="col-7">
        <h2 class="mt-9">How It Works</h2>
      </div>
      <v-btn class="mt-3 ml-3" icon @click="close()"><v-icon>mdi-close</v-icon></v-btn>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Emit, Vue } from 'vue-property-decorator'

@Component({})
export default class LearnMoreBCSC extends Vue {
  private isDialogOpen = false

  public open () {
    this.isDialogOpen = true
  }

  public close () {
    this.isDialogOpen = false
  }

  @Emit('bcsc-selected')
  private select () {
    this.close()
  }
}
</script>

<style lang="scss" scoped>
  li {
    margin-top: 3em;
    margin-bottom: 3em;
  }
</style>
