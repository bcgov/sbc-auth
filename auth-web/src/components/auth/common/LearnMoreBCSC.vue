<template>
  <v-dialog
    v-model="isDialogOpen"
    content-class="learn-more-dialog"
    :fullscreen="$vuetify.breakpoint.xs || $vuetify.breakpoint.sm"
  >
    <v-card class="learn-more-content d-flex">
      <!-- Left Panel -->
      <div class="left-panel flex-grow-0 flex-shrink-0 pa-8">
        <div class="body-2 font-weight-bold text-uppercase text--secondary mb-5">
          Authentication Options
        </div>
        <h1 class="mb-8">
          BC Services Card
        </h1>
        <ul class="mb-11">
          <li class="mb-5">
            The BC Services Card enables safe and secure access to government digital services.
            BC residents may have the combined Driver's License or a stand-alone Services Card.
          </li>
          <li class="mb-5">
            Registries only ever accesses your name and surname.
            We never access health, driving, or any other personal information.
          </li>
          <li>
            There are two options for logging in with the BC Services Card.
            Review the diagrams on this screen for information on how they work.
          </li>
        </ul>
        <v-btn
          large
          block
          color="primary"
          class="font-weight-bold"
          @click="select()"
        >
          SELECT
        </v-btn>
      </div>

      <v-divider vertical />

      <!-- Right Panel -->
      <div class="pa-8">
        <h2 class="mt-n1 mb-9">
          How It works - Mobile Card
        </h2>
        <ul class="steps">
          <li>
            <div class="step-content">
              <v-img
                contain
                class="step-img"
                :src="mobileDownloadImageSrc"
                alt="Download the BC Services Card app"
              >
                <template #placeholder>
                  <v-row
                    class="fill-height ma-0"
                    align="center"
                    justify="center"
                  >
                    <v-progress-circular
                      indeterminate
                      color="primary lighten-5"
                    />
                  </v-row>
                </template>
              </v-img>
              <div class="step-line mt-2" />
              <div class="step-text body-2 mt-3 mb-8">
                Download the BC Services Card app and choose "Set up Mobile Card".
              </div>
            </div>
          </li>
          <li>
            <div class="step-content">
              <v-img
                contain
                class="step-img"
                :src="bcscCodeImageSrc"
                alt="Scan or enter serial number"
              >
                <template #placeholder>
                  <v-row
                    class="fill-height ma-0"
                    align="center"
                    justify="center"
                  >
                    <v-progress-circular
                      indeterminate
                      color="grey"
                    />
                  </v-row>
                </template>
              </v-img>
              <div class="step-line mt-2" />
              <div class="step-text body-2 mt-3 mb-8">
                Scan or enter the barcode on the back of your card with the app and enter your birthdate.
              </div>
            </div>
          </li>
          <li>
            <div class="step-content">
              <v-img
                contain
                class="step-img"
                :src="verifyIdentityImageSrc"
                alt="Verify your card"
              >
                <template #placeholder>
                  <v-row
                    class="fill-height ma-0"
                    align="center"
                    justify="center"
                  >
                    <v-progress-circular
                      indeterminate
                      color="grey"
                    />
                  </v-row>
                </template>
              </v-img>
              <div class="step-line mt-2" />
              <div class="step-text body-2 mt-3 mb-8">
                Complete a one-time security check by video or in person to verify your identity.
              </div>
            </div>
          </li>
          <li>
            <div class="step-content">
              <v-img
                contain
                class="step-img"
                :src="loginImageSrc"
                alt="Log in to BC Registries"
              >
                <template #placeholder>
                  <v-row
                    class="fill-height ma-0"
                    align="center"
                    justify="center"
                  >
                    <v-progress-circular
                      indeterminate
                      color="grey"
                    />
                  </v-row>
                </template>
              </v-img>
              <div class="step-line mt-2" />
              <div class="step-text body-2 mt-3 mb-8">
                Log in to BC Registries using the BC Services Card option, and select "Use a Mobile Card".
              </div>
            </div>
          </li>
          <li>
            <div class="step-content">
              <v-img
                contain
                class="step-img"
                :src="mobileCodeImageSrc"
                alt="Choose mobile card and get pairing code"
              >
                <template #placeholder>
                  <v-row
                    class="fill-height ma-0"
                    align="center"
                    justify="center"
                  >
                    <v-progress-circular
                      indeterminate
                      color="grey"
                    />
                  </v-row>
                </template>
              </v-img>
              <div class="step-line mt-2" />
              <div class="step-text body-2 mt-3 mb-8">
                Open the BC Services Card app and enter the pairing code you see on the website.
              </div>
            </div>
          </li>
          <li>
            <div class="step-content">
              <v-img
                class="step-img"
                :src="userProfileImageSrc"
                alt="Agree to terms and create user profile"
              >
                <template #placeholder>
                  <v-row
                    class="fill-height ma-0"
                    align="center"
                    justify="center"
                  >
                    <v-progress-circular
                      indeterminate
                      color="grey"
                    />
                  </v-row>
                </template>
              </v-img>
              <div class="step-line mt-2" />
              <div class="step-text body-2 mt-3 mb-8">
                Agree to terms of use, create user profile.
              </div>
            </div>
          </li>
          <li>
            <div class="step-content">
              <v-img
                contain
                class="step-img"
                :src="successImageSrc"
                alt="Continue to system"
              >
                <template #placeholder>
                  <v-row
                    class="fill-height ma-0"
                    align="center"
                    justify="center"
                  >
                    <v-progress-circular
                      indeterminate
                      color="grey"
                    />
                  </v-row>
                </template>
              </v-img>
              <div class="step-line mt-2" />
              <div class="step-text body-2 mt-3">
                Continue to BC Registries.
              </div>
            </div>
          </li>
        </ul>

        <v-divider />

        <h2 class="mt-8 mb-9">
          How it works - Card Reader
        </h2>
        <ul class="steps">
          <li>
            <div class="step-content">
              <v-img
                contain
                class="step-img"
                :src="personDeskImageSrc"
                alt="Visit a Service BC Centre"
              >
                <template #placeholder>
                  <v-row
                    class="fill-height ma-0"
                    align="center"
                    justify="center"
                  >
                    <v-progress-circular
                      indeterminate
                      color="grey"
                    />
                  </v-row>
                </template>
              </v-img>
              <div class="step-line mt-2" />
              <div class="step-text body-2 mt-3 mb-8">
                Visit a Service BC centre to obtain a government-issued USB card reader and passcode.
              </div>
            </div>
          </li>
          <li>
            <div class="step-content">
              <v-img
                contain
                class="step-img"
                :src="loginImageSrc"
                alt="Log in to BC Registries"
              >
                <template #placeholder>
                  <v-row
                    class="fill-height ma-0"
                    align="center"
                    justify="center"
                  >
                    <v-progress-circular
                      indeterminate
                      color="grey"
                    />
                  </v-row>
                </template>
              </v-img>
              <div class="step-line mt-2" />
              <div class="step-text body-2 mt-3 mb-8">
                Log in to BC Registries using the BC Services Card option.
              </div>
            </div>
          </li>
          <li>
            <div class="step-content">
              <v-img
                contain
                class="step-img"
                :src="usbKeyImageSrc"
                alt="Choose USB Card Reader option"
              >
                <template #placeholder>
                  <v-row
                    class="fill-height ma-0"
                    align="center"
                    justify="center"
                  >
                    <v-progress-circular
                      indeterminate
                      color="grey"
                    />
                  </v-row>
                </template>
              </v-img>
              <div class="step-line mt-2" />
              <div class="step-text body-2 mt-3 mb-8">
                Choose the USB card reader option.
              </div>
            </div>
          </li>
          <li>
            <div class="step-content">
              <v-img
                contain
                class="step-img"
                :src="desktopDownloadImageSrc"
                alt="Download and install desktop app"
              >
                <template #placeholder>
                  <v-row
                    class="fill-height ma-0"
                    align="center"
                    justify="center"
                  >
                    <v-progress-circular
                      indeterminate
                      color="grey"
                    />
                  </v-row>
                </template>
              </v-img>
              <div class="step-line mt-2" />
              <div class="step-text body-2 mt-3 mb-8">
                Download and install the BC Services Card Reader software, then insert the USB card reader.
              </div>
            </div>
          </li>
          <li>
            <div class="step-content">
              <v-img
                contain
                class="step-img"
                :src="usbCardImageSrc"
                alt="Hold card against USB card reader"
              >
                <template #placeholder>
                  <v-row
                    class="fill-height ma-0"
                    align="center"
                    justify="center"
                  >
                    <v-progress-circular
                      indeterminate
                      color="grey"
                    />
                  </v-row>
                </template>
              </v-img>
              <div class="step-line mt-2" />
              <div class="step-text body-2 mt-3">
                Open the BC Services Card Reader software and hold card flat against the USB card reader until a success notification appears.
              </div>
            </div>
          </li>
          <li>
            <div class="step-content">
              <v-img
                contain
                class="step-img"
                :src="desktopCodeImageSrc"
                alt="Enter passcode"
              >
                <template #placeholder>
                  <v-row
                    class="fill-height ma-0"
                    align="center"
                    justify="center"
                  >
                    <v-progress-circular
                      indeterminate
                      color="grey"
                    />
                  </v-row>
                </template>
              </v-img>
              <div class="step-line mt-2" />
              <div class="step-text body-2 mt-3">
                Enter your passcode.
              </div>
            </div>
          </li>
          <li>
            <div class="step-content">
              <v-img
                class="step-img"
                :src="userProfileImageSrc"
                alt="Agree to terms and create user profile"
              >
                <template #placeholder>
                  <v-row
                    class="fill-height ma-0"
                    align="center"
                    justify="center"
                  >
                    <v-progress-circular
                      indeterminate
                      color="grey"
                    />
                  </v-row>
                </template>
              </v-img>
              <div class="step-line mt-2" />
              <div class="step-text body-2 mt-3 mb-8">
                Agree to terms of use, create user profile.
              </div>
            </div>
          </li>
          <li>
            <div class="step-content">
              <v-img
                contain
                class="step-img"
                :src="successImageSrc"
                alt="Continue to system"
              >
                <template #placeholder>
                  <v-row
                    class="fill-height ma-0"
                    align="center"
                    justify="center"
                  >
                    <v-progress-circular
                      indeterminate
                      color="grey"
                    />
                  </v-row>
                </template>
              </v-img>
              <div class="step-line mt-2" />
              <div class="step-text body-2 mt-3">
                Continue to BC Registries.
              </div>
            </div>
          </li>
        </ul>
      </div>
      <v-btn
        large
        icon
        class="close-btn"
        @click="close()"
      >
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Emit, Vue } from 'vue-property-decorator'

@Component({})
export default class LearnMoreBCSC extends Vue {
  isDialogOpen = false

  readonly mobileDownloadImageSrc = new URL('@/assets/img/learn-more/mobile-download.jpg', import.meta.url)
  readonly bcscCodeImageSrc = new URL('@/assets/img/learn-more/bcsc-code.jpg', import.meta.url)
  readonly verifyIdentityImageSrc = new URL('@/assets/img/learn-more/verify-identity.jpg', import.meta.url)
  readonly logInImageSrc = new URL('@/assets/img/learn-more/log-in.jpg', import.meta.url)
  readonly mobileCodeImageSrc = new URL('@/assets/img/learn-more/mobile-code.jpg', import.meta.url)
  readonly userProfileImageSrc = new URL('@/assets/img/learn-more/user-profile.jpg', import.meta.url)
  readonly successImageSrc = new URL('@/assets/img/learn-more/success.jpg', import.meta.url)
  readonly personDeskImageSrc = new URL('@/assets/img/learn-more/person-desk.jpg', import.meta.url)
  readonly loginImageSrc = new URL('@/assets/img/learn-more/login.jpg', import.meta.url)
  readonly usbKeyImageSrc = new URL('@/assets/img/learn-more/usb-key.jpg', import.meta.url)
  readonly desktopDownloadImageSrc = new URL('@/assets/img/learn-more/desktop-download.jpg', import.meta.url)
  readonly usbCardImageSrc = new URL('@/assets/img/learn-more/usb-card.jpg', import.meta.url)
  readonly desktopCodeImageSrc = new URL('@/assets/img/learn-more/desktop-code.jpg', import.meta.url)

  public open () {
    this.isDialogOpen = true
  }

  public close () {
    this.isDialogOpen = false
  }

  @Emit('bcsc-selected')
  select () {
    this.close()
  }
}
</script>

<style lang="scss" scoped>
  $step-content-width: 10.5rem;

  ::v-deep .learn-more-dialog {
    max-width: 1600px;
  }

  .learn-more-content {
    flex-direction: row;

    .left-panel {
      flex: 0 0 auto;
      width: 25rem;
    }
  }

  .v-dialog--fullscreen .learn-more-content {
    flex-direction: column;
    border-radius: 0 !important;

    .left-panel {
      flex: 1 1 auto;
      width: auto;
      border-bottom: 1px solid var(--v-grey-lighten2)
    }
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
    background-color: var(--v-grey-lighten4);
  }

  .step-text {
    text-align: center;
  }

  .step-line {
    position: relative;
    height: 8px;
    background: gold;

    &::before {
      content: ' ';
      position: absolute;
      bottom: 0;
      left: -3rem;
      width: 2rem;
      height: 8px;
      background: #666;
    }

    &::after {
      content: ' ';
      position: absolute;
      left: -1.5rem;
      bottom: -7px;
      width: 1rem;
      height: 22px;
      border-style: solid;
      border-width: 11px 0 11px 11px;
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
