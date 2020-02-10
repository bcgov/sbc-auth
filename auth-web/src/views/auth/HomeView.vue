<template>
  <div>
    <article>
      <header class="hero-banner light">
        <v-container>
          <v-row>
            <v-col cols="12" lg="8">
              <h1>Welcome to Cooperatives Online<sup>Beta</sup></h1>
              <p>File your BC cooperative association's annual reports and maintain your registered office addresses and director information.</p>

              <div class="hero-banner__cta-btns">
                <!-- Authenticated -->
                <div v-if="userProfile">
                  <v-btn large color="#fcba19" class="cta-btn"
                    to="/main">
                    Manage Businesses
                  </v-btn>
                  <v-btn large color="#fcba19" class="cta-btn">
                    Create a New BC Registries Account
                  </v-btn>
                </div>

                <!-- Non-authenticated -->
                <v-btn large color="#fcba19" class="cta-btn"
                  v-if="!userProfile"
                  @click="accountDialog = true">
                  Create a BC Registries Account
                </v-btn>
              </div>

              <v-dialog v-model="accountDialog" max-width="640">
                <v-card>
                  <v-card-title>Create a BC Registries Account</v-card-title>
                  <v-card-text>
                    To create a BC Registries account you will need to log in using your BC Services Card, the government of British Columbia's trusted way to access online services.
                  </v-card-text>
                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn large color="primary" @click="login()">Log in</v-btn>
                    <v-btn large depressed color="default" @click="accountDialog = false">Cancel</v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
            </v-col>
          </v-row>
        </v-container>
      </header>
      <div class="how-to-container">
        <v-container>
          <section>
            <h2>How do I file?</h2>
            <section>
              <v-card flat class="section-card">
                <v-row>
                  <v-col sm="12" md="8" class="section-card__inner">
                    <div class="section-card__icon">
                      <v-icon>mdi-shield-check</v-icon>
                    </div>
                    <div class="section-card__text">
                      <h3>1. &nbsp;Log in with your BC Services Card</h3>
                      <p class="mb-0">You must securely log in with your BC Services Card, government’s trusted way to access online services. It typically takes five minutes or less to <a href="https://www2.gov.bc.ca/gov/content/governments/government-id/bc-services-card/login-with-card/mobile-card/set-up-mobile-card" target="_blank">set up</a> your mobile card, and the only information BC Registries can access from your card is your legal name.</p>
                    </div>
                  </v-col>
                  <v-col sm="12" md="4" class="section-card__links">
                    <ul class="mb-0">
                      <li>
                        <v-btn text color="primary" href="https://www2.gov.bc.ca/gov/content/governments/government-id/bc-services-card" target="_blank" rel="noopener">
                          <v-icon small>mdi-open-in-new</v-icon>
                          <span>What is a BC <span class="nobr">Services Card?</span></span>
                        </v-btn>
                      </li>
                      <li>
                        <v-btn text color="primary" href="https://www2.gov.bc.ca/gov/content/governments/government-id/bc-services-card/login-with-card" target="_blank" rel="noopener">
                          <v-icon small>mdi-open-in-new</v-icon>
                          <span>How do I log in with my BC <span class="nobr">Services Card?</span></span>
                        </v-btn>
                      </li>
                      <li>
                        <v-btn text color="primary" href="https://www2.gov.bc.ca/gov/content/governments/government-id/bc-services-card/get-a-card" target="_blank" rel="noopener">
                          <v-icon small>mdi-open-in-new</v-icon>
                          <span>I don't have a BC <span class="nobr">Services Card</span></span>
                        </v-btn>
                      </li>
                    </ul>
                  </v-col>
                </v-row>
              </v-card>
            </section>
            <section>
              <v-card flat class="section-card">
                <v-row>
                  <v-col sm="12" md="8" class="section-card__inner">
                    <div class="section-card__icon">
                      <v-icon>mdi-lock-open</v-icon>
                    </div>
                    <div class="section-card__text">
                      <h3>2. &nbsp;Authorize to file for a cooperative</h3>
                      <p class="mb-0">You will need to authorize to manage a cooperative by providing the <strong>Incorporation Number</strong> and <strong>Passcode</strong> located in the <strong>Access Letter</strong> you received in the mail from BC Registries.</p>
                    </div>
                  </v-col>
                  <v-col sm="12" md="4" class="section-card__links">
                    <ul class="mb-0">
                      <li>
                        <v-btn text color="primary" @click.stop="noPasscodeDialog = true">
                          <v-icon small>mdi-open-in-new</v-icon>
                          <span>I lost or forgot my cooperative passcode</span>
                        </v-btn>
                      </li>
                      <li>
                        <v-btn text color="primary" @click.stop="noPasscodeDialog = true">
                          <v-icon small>mdi-open-in-new</v-icon>
                          <span>I didn't receive my <span class="nobr">Access Letter</span></span>
                        </v-btn>
                      </li>
                    </ul>

                    <!-- No Passcode Dialog -->
                    <v-dialog width="640" v-model="noPasscodeDialog">
                      <v-card>
                        <v-card-title>Don't have a Passcode?</v-card-title>
                        <v-card-text>
                          <p class="mb-7">If you have not received your Access Letter from BC Registries, or have lost your Passcode, please contact us at:</p>
                          <ul class="contact-info__list mb-7">
                            <li>
                              <span>Toll Free:</span> {{ $t('techSupportTollFree') }}
                            </li>
                            <li>
                              <span>Phone:</span> {{ $t('techSupportPhone') }}
                            </li>
                            <li>
                              <span>Email:</span> <a v-bind:href="'mailto:' + $t('techSupportEmail') + '?subject=' + $t('techSupportEmailSubject')">{{ $t('techSupportEmail') }}</a>
                            </li>
                          </ul>
                          <div>
                            <p class="mb-0"><strong>Hours of Operation:</strong><br>Monday to Friday, 8:30am - 4:30pm <span title="Pacific Standard Time">PST</span></p>
                          </div>
                        </v-card-text>
                        <v-card-actions>
                          <v-spacer></v-spacer>
                          <v-btn large depressed color="primary" @click="noPasscodeDialog = false">OK</v-btn>
                        </v-card-actions>
                      </v-card>
                    </v-dialog>

                  </v-col>
                </v-row>
              </v-card>
            </section>
            <section>
              <v-card flat class="section-card">
                <v-row>
                  <v-col sm="12" md="8" class="section-card__inner">
                    <div class="section-card__icon">
                      <v-icon>mdi-clipboard-check</v-icon>
                    </div>
                    <div class="section-card__text">
                      <h3>3. &nbsp;Complete your cooperative's filings</h3>
                      <p class="mb-0">Once you have logged in and are authorized to manage a cooperative, simply click on the cooperative you want to do work for, and complete your filings.</p>
                    </div>
                  </v-col>
                  <v-col sm="12" md="4" class="section-card__links">
                    <ul class="static-links mb-0">
                      <li>
                        <v-icon small>mdi-check</v-icon>
                        <span>Annual Reports</span>
                      </li>
                      <li>
                        <v-icon small>mdi-check</v-icon>
                        <span>Manage Office Addresses</span>
                      </li>
                      <li>
                        <v-icon small>mdi-check</v-icon>
                        <span>Manage Director Information</span>
                      </li>
                    </ul>
                  </v-col>
                </v-row>
              </v-card>

              <div class="cta-container">
                <v-btn large color="#fcba19" class="cta-btn" active-class="cta-btn--active" to="/main" v-if="userProfile">Manage Businesses</v-btn>
                <v-btn large color="#fcba19" class="cta-btn" active-class="cta-btn--active" to="/signin/bcsc" v-if="!userProfile">Log in with BC Services Card</v-btn>
              </div>

            </section>
          </section>
        </v-container>
      </div>
      <div class="contact-info-container light">
        <v-container>
          <v-row>
            <v-col sm="12" md="8">
              <h3 class="mb-6">Need more information?</h3>
              <p class="mb-4">To learn more about Cooperative Associations in British Columbia, please visit the Cooperative Associations information page on the <a href="https://www2.gov.bc.ca/gov/content/employment-business/business/managing-a-business/permits-licences/businesses-incorporated-companies/cooperative-associations" target="_blank" rel="noopener">BC Government website</a>.</p>
            </v-col>

            <v-col sm="12" md="4">
              <h3 class="mb-6">Contact Us</h3>
              <p class="mb-5">For support or questions about this application, contact us at:</p>
              <ul class="contact-info__list mb-5">
                <li><span>Toll Free:</span> {{ $t('techSupportTollFree') }}</li>
                <li><span>Phone:</span> {{ $t('techSupportPhone') }}</li>
                <li><span>Email:</span> <a href="mailto:bcregistries@gov.bc.ca?subject=BC Registries - Cooperatives Online Support Request">bcregistries@gov.bc.ca</a></li>
              </ul>
              <p class="mb-0"><strong>Hours of Operation:</strong><br>Monday to Friday, 8:30am - 4:30pm <span title="Pacific Standard Time">PST</span></p>
            </v-col>
          </v-row>
        </v-container>
      </div>
    </article>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import { User } from '@/models/user'
import { VueConstructor } from 'vue'

@Component({
  name: 'Home',
  computed: {
    ...mapState('user', ['userProfile'])
  }
})

export default class HomeView extends Vue {
  private readonly userProfile!: User
  private readonly getUserProfile!: (identifier: string) => User
  private noPasscodeDialog = false
  private accountDialog = false

  login () {
    window.location.assign('/cooperatives/auth/signin/bcsc')
  }
}
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";

  article {
    padding: 0;
  }

  section + section {
    margin-top: 1rem;
  }

  h2 {
    margin-bottom: 2.5rem;
    font-size: 2rem;
  }

  // Hero Banner
  .hero-banner {
    h1 {
      margin-bottom: 1.5rem;
      letter-spacing: -0.06rem;
      line-height: 1.25;
      font-size: 2.75rem;

      sup {
        top: -0.9rem;
        margin-left: 0.25rem;
        vertical-align: middle;
        color: $gray7;
        text-transform: uppercase;
        letter-spacing: 0.05rem;
        font-size: .875rem;
      }
    }

    p {
      margin-bottom: 2.5rem;
      font-size: 1.125rem;
    }

    .container {
      padding-top: 2.25rem;
      padding-bottom: 3.25rem;
    }
  }

  .hero-banner__cta-btns {
    .cta-btn + .cta-btn {
      margin-left: 0.5rem;
    }
  }

  @media (max-width: 1200px) {
    .hero-banner {
      text-align: center;

      p {
        margin: 0 auto;
        max-width: 40rem;
      }
    }
  }

  // How to Section
  .how-to-container {
    background: rgb(248,249,250);
    background: radial-gradient(circle, $gray1 25%, $gray3 100%);

    .container {
      padding-top: 2.5rem;
      padding-bottom: 3.5rem;
    }

    h2 {
      text-align: center;
    }
  }

  // Section Cards
  .section-card {
    padding-top: 1.75rem;
    padding-bottom: 2rem;

    h3 {
      margin-bottom: 1.25rem;
      font-size: 1.5rem;
      font-weight: 700;
    }

    p {
      color: $gray7;
    }
  }

  .section-card__inner {
    display: flex;
    flex-direction: row;
  }

  // Variables
  $section-card-icon-width: 9rem;

  .section-card__icon {
    flex: 0 0 auto;
    position: relative;
    width: $section-card-icon-width;
    text-align: center;

    .v-icon {
      margin-top: -0.65rem;
      color: $BCgovGold5;
      font-size: 4rem;
    }

    .step {
      margin: 0.5rem 0;
      text-align: center;
      text-transform: uppercase;
      font-size: 0.875rem;
      font-weight: 700;
    }
  }

  .section-card__text {
    padding-right: 2rem;
  }

  .section-card__links {
    padding-right: 2rem;

    ul {
      padding: 0;
      list-style-type: none;
    }

    ::v-deep .v-btn__content {
      align-items: flex-start;
    }

    .v-btn {
      height: auto !important;
      display: inline-block;
      padding: 0.5rem 1rem !important;
      white-space: normal;
      font-weight: 700;

      .v-icon {
        margin-top: 0.1rem;
        margin-right: 0.75rem;
      }

      span {
        text-decoration: underline;
      }
    }
  }

  @media (max-width: 960px) {
    .section-card__links {
      padding-bottom: 0;

      ul {
        margin-left: $section-card-icon-width;
      }
    }
  }

  .static-links {
    li {
      display: flex;
      align-items: flex-start;
      padding: 0.4rem 1rem;
      color: $gray6;
      font-size: 0.875rem;
      font-weight: 700;

      .v-icon {
        margin-top: 0.2rem;
        margin-left: -0.5rem;
        margin-right: 0.75rem;
      }
    }
  }

  // Contact Section
  .contact-info-container {
    .container {
      padding-top: 2rem;
      padding-bottom: 2.5rem;
    }

    h3 {
      margin-bottom: 1rem;
      padding-bottom: 0.5rem;
      border-bottom: 2px solid $gray3;
      font-size: 1.5rem;
    }
  }

  .contact-info__list {
    margin: 0;
    padding: 0;
    list-style-type: none;

    li {
      strong, span {
        margin-right: 0.5rem;
      }
    }
  }

  @media (max-width: 960px) {
    .contact-info-container {
      text-align: center;
    }
  }

  .cta-container {
    margin-top: 3rem;
    text-align: center;
  }

  .v-btn.cta-btn {
    color: $BCgovBlue5;
    font-weight: 700;
  }

  // Helper Classes
  .dark {
    background-color: $BCgovBlue5;

    h1, p {
      color: $gray0;
    }
  }

  .light {
    background-color: #ffffff;
  }

  // Fix initial display of the dialog container
  .v-dialog__container {
    display: none;
  }
</style>
