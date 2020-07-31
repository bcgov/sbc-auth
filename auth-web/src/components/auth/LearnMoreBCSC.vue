<template>
  <v-dialog content-class="learn-more-dialog" v-model="isDialogOpen">
    <v-card class="d-flex">

      <!-- Left Panel -->
      <div class="left-panel flex-grow-0 flex-shrink-0 pa-10">
        <div class="body-2 font-weight-bold text-uppercase text--secondary mb-5">Authentication Options</div>
        <h1 class="mb-8">
          BC Services Card
        </h1>
        <ul class="mb-11">
          <li class="mb-5">The BC Services Card enables safe and secure access to government digital services. BC residents may have the combined Driver's License or a stand-alone Services Card.</li>
          <li class="mb-5">Registries only ever accesses your name and surname. We never access health, driving, or any other personal information.</li>
          <li>There are two options for logging in with the BC Services Card. Review the diagrams on this screen for information on how they work.</li>
        </ul>
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
      </div>

      <v-divider vertical />

      <!-- Right Panel -->
      <div class="pa-10">
        <h2 class="mt-n1 mb-11">How It works - Mobile Card</h2>
        <ul class="steps">
          <li>
            <div class="step-content">
             <v-img src="@/assets/img/learn-more/mobile-download.jpg" alt="Download the BC Services Card app"></v-img>
              <div class="step-line mt-2">
              </div>
              <div class="step-text body-2 mt-3 mb-8">
                Download the BC Services Card app and choose 'add card'.
              </div>
            </div>
          </li>
          <li>
            <div class="step-content">
             <v-img src="@/assets/img/learn-more/bcsc-code.jpg" alt="Scan or enter serial number"></v-img>
              <div class="step-line mt-2">
              </div>
              <div class="step-text body-2 mt-3 mb-8">
                Enter your card by scanning or entering your serial number.
              </div>
            </div>
          </li>
          <li>
            <div class="step-content">
             <v-img src="@/assets/img/learn-more/verify-identity.jpg" alt="Verify your card"></v-img>
              <div class="step-line mt-2">
              </div>
              <div class="step-text body-2 mt-3 mb-8">
                Verify your card either through a video call or in-person at a Service BC location.
              </div>
            </div>
          </li>
          <li>
            <div class="step-content">
             <v-img src="@/assets/img/learn-more/log-in.jpg" alt="Log in to BC Registries"></v-img>
              <div class="step-line mt-2">
              </div>
              <div class="step-text body-2 mt-3 mb-8">
                Log in via BC Registries
              </div>
            </div>
          </li>
          <li>
            <div class="step-content">
             <v-img src="@/assets/img/learn-more/mobile-code.jpg" alt="Choose mobile card and get pairing code"></v-img>
              <div class="step-line mt-2">
              </div>
              <div class="step-text body-2 mt-3 mb-8">
                Choose to use a 'Mobile card' and get a pairing code
              </div>
            </div>
          </li>
          <li>
            <div class="step-content">
             <v-img src="@/assets/img/learn-more/success.jpg" alt="Continue to system"></v-img>
              <div class="step-line mt-2">
              </div>
              <div class="step-text body-2 mt-3">
                Once logged in, continue to system.
              </div>
            </div>
          </li>
        </ul>
        <h2 class="my-11">How it works - Card Reader</h2>
        <ul class="steps">
          <li>
            <div class="step-content">
             <v-img class="step-img" src="@/assets/img/learn-more/person-desk.jpg" alt="Visit a Service BC Centre"></v-img>
              <div class="step-line mt-2">
              </div>
              <div class="step-text body-2 mt-3 mb-8">
                Visit a Service BC centre to obtain a government-issued USB card reader and passcode.
              </div>
            </div>
          </li>
          <li>
            <div class="step-content">
             <v-img class="step-img" src="@/assets/img/learn-more/log-in.jpg" alt="Log in to BC Registries"></v-img>
              <div class="step-line mt-2">
              </div>
              <div class="step-text body-2 mt-3 mb-8">
                Log in to BC Registries using the BC Services Card option.
              </div>
            </div>
          </li>
          <li>
            <div class="step-content">
             <v-img class="step-img" src="@/assets/img/learn-more/usb-key.jpg" alt="Choose USB Card Reader option"></v-img>
              <div class="step-line mt-2">
              </div>
              <div class="step-text body-2 mt-3 mb-8">
                Choose the USB card reader option.
              </div>
            </div>
          </li>
          <li>
            <div class="step-content">
             <v-img class="step-img" src="@/assets/img/learn-more/desktop-download.jpg" alt="Download and install desktop app"></v-img>
              <div class="step-line mt-2">
              </div>
              <div class="step-text body-2 mt-3 mb-8">
                Download and install the desktop app, promoted when you insert the usb key.
              </div>
            </div>
          </li>
          <li>
            <div class="step-content">
              <v-img class="step-img" src="@/assets/img/learn-more/usb-card.jpg" alt="Hold card against USB card reader"></v-img>
              <div class="step-line mt-2">
              </div>
              <div class="step-text body-2 mt-3">
                Open the app and hold card flat against the USB card reader until a success notification appears.
              </div>
            </div>
          </li>
          <li>
            <div class="step-content">
              <v-img class="step-img" src="@/assets/img/learn-more/desktop-code.jpg" alt="Enter passcode"></v-img>
              <div class="step-line mt-2">
              </div>
              <div class="step-text body-2 mt-3">
                Enter your passcode.
              </div>
            </div>
          </li>
          <li>
            <div class="step-content">
              <v-img class="step-img" src="@/assets/img/learn-more/success.jpg" alt="Continue to system"></v-img>
              <div class="step-line mt-2">
              </div>
              <div class="step-text body-2 mt-3">
                Once logged in, continue to system.
              </div>
            </div>
          </li>
        </ul>
      </div>
      <v-btn
        large
        icon
        class="close-btn"
        @click="close()">
        <v-icon>mdi-close</v-icon>
      </v-btn>
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
  $step-content-width: 9.5rem;
  $step-line-height: 6px;

  ::v-deep .learn-more-dialog {
    max-width: 1400px;
  }

  .left-panel {
    width: 25rem;
  }

  .steps {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    margin: 0 -1rem;
    padding: 0;
    list-style-type: none;

    li {
      flex: 0 0 auto;
      position: relative;
      margin: 0 2rem;
      max-width: 25%;
      vertical-align: top;
    }
  }

  .step-content {
    width: $step-content-width;
    margin: 0 auto;
  }

  .step-img {
    width: $step-content-width;
    height: $step-content-width;
  }

  .step-text {
    text-align: center;
  }

  .step-line {
    position: relative;
    height: $step-line-height;
    background: gold;

    &::before {
      content: ' ';
      position: absolute;
      bottom: 0;
      left: -3rem;
      width: 1.5rem;
      height: $step-line-height;
      background: #666;
    }

    &::after {
      content: ' ';
      position: absolute;
      left: -1.5rem;
      bottom: -5px;
      width: 16px;
      height: 16px;
      border-style: solid;
      border-width: 8px 0 8px 8px;
      border-color: transparent transparent transparent #666;
    }
  }

  .steps li:first-child {
    .step-line {
      &::before,
      &::after {
        display: none;
      }
    }
  }

  .close-btn {
    position: absolute;
    top: 1rem;
    right: 1rem;
  }
</style>
