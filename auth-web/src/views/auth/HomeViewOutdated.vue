<template>
  <div>
    <article>
      <v-alert color="grey lighten-3" class="covid-alert">
        <v-container>
          <p class="title font-weight-bold">Special Notice Regarding COVID-19 and Annual General Meetings</p>
          <p>In these uncertain times, it is important that individuals and organizations follow the guidelines
            and recommendations set forth by the Provincial Health Officer and B.C. Health Minister, as well as
            Health Canada guidelines in regards to the novel coronavirus (COVID-19). Due to these guidelines, the
            Registrar has decided to grant an extension for all Cooperatives that wish to delay their Annual General
            Meeting (AGM) for a period of six months from March 31, 2020 to September 30, 2020.</p>
          <p>You do not need to make an application to the registrar to request a delay of your AGM; however, you
            must inform your members that the AGM has been delayed.</p>
        </v-container>
      </v-alert>

      <header class="hero-banner">
        <v-container>
          <h1>Welcome to Business Registry<sup>Beta</sup></h1>
          <p>File your BC cooperative association's annual reports and maintain your registered office addresses and director information.</p>

          <div class="hero-banner__cta-btns">
            <!-- Authenticated -->
            <div v-if="userProfile">
              <v-btn large color="#fcba19" class="cta-btn"
                @click="goToManageBusinesses()">
                Manage Businesses
              </v-btn>
              <v-btn large outlined color="#ffffff"
                class="cta-btn"
                v-if="!isDirSearchUser" to="/choose-authentication-method">
                Create a new BC Registries Account
              </v-btn>
            </div>

            <!-- Non-authenticated -->
            <v-btn large color="#fcba19" class="cta-btn"
              v-if="!userProfile" to="/choose-authentication-method">
              Create a BC Registries Account
            </v-btn>
          </div>

          <v-dialog v-model="accountDialog" max-width="640">
            <LoginBCSC>
              <template v-slot:actions>
                <v-btn large color="primary" @click="login()">Log in</v-btn>
                <v-btn large depressed color="default" @click="accountDialog = false">Cancel</v-btn>
              </template>
            </LoginBCSC>
          </v-dialog>

          <v-dialog v-model="oopDialog" max-width="740">
            <OutOfProvinceDialog
              @close="oopDialog = false"
              @oop = "goToOutOfProvince()"
              @bc-not-signed-in = "oopDialog = false; accountDialog = true"
              @bc-signed-in = "createAccount()"
              :signed-in = "!!userProfile"
            />
          </v-dialog>

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
                      <p class="mb-0">You must securely log in with your BC Services Card, government’s trusted way to access online services. It typically takes five minutes or less to <a href="https://www2.gov.bc.ca/gov/content/governments/government-id/bc-services-card/log-in-with-card/mobile-card/set-up-mobile-card" target="_blank" rel="noopener noreferrer">set up</a> your mobile card, and the only information BC Registries can access from your card is your legal name.</p>
                    </div>
                  </v-col>
                  <v-col sm="12" md="4" class="section-card__links">
                    <ul class="mb-0">
                      <li>
                        <v-btn text color="primary" href="https://www2.gov.bc.ca/gov/content/governments/government-id/bc-services-card/log-in-with-card/mobile-card" target="_blank" rel="noopener noreferrer">
                          <v-icon small>mdi-open-in-new</v-icon>
                          <span>What is a Mobile BC <span class="nobr">Services Card?</span></span>
                        </v-btn>
                      </li>
                      <li>
                        <v-btn text color="primary" href="https://www2.gov.bc.ca/gov/content/governments/government-id/bc-services-card/log-in-with-card/mobile-card/login-with-mobile-card" target="_blank" rel="noopener noreferrer">
                          <v-icon small>mdi-open-in-new</v-icon>
                          <span>How do I log in with my BC <span class="nobr">Services Card?</span></span>
                        </v-btn>
                      </li>
                      <li>
                        <v-btn text color="primary" href="https://www2.gov.bc.ca/gov/content/governments/government-id/bc-services-card/get-a-card" target="_blank" rel="noopener noreferrer">
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
                          <p class="mb-7"><strong>Hours of Operation:</strong><br>Monday to Friday, 8:30am - 4:30pm <span title="Pacific Standard Time">PST</span></p>
                          <a class="link-w-icon" href="https://www2.gov.bc.ca/gov/content/employment-business/business/managing-a-business/permits-licences/news-updates/modernization/coops-services-card"
                             target="_blank" rel="noopener noreferrer">
                            <v-icon small class="mr-2">mdi-open-in-new</v-icon>
                            <span>Frequently Asked Questions</span>
                          </a>
                        </v-card-text>
                        <v-card-actions>
                          <v-spacer></v-spacer>
                          <v-btn large color="primary" @click="noPasscodeDialog = false">OK</v-btn>
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
                <v-btn large color="#fcba19" class="cta-btn" active-class="cta-btn--active" @click="goToManageBusinesses()" v-if="userProfile">Manage Businesses</v-btn>
                <v-btn large color="#fcba19" class="cta-btn" active-class="cta-btn--active" @click="login()" v-if="!userProfile">Log in with BC Services Card</v-btn>
              </div>

            </section>
          </section>
        </v-container>
      </div>
      <div class="contact-info-container">
        <v-container>
          <v-row>
            <v-col cols="12" md="8">
              <h3 class="mb-6">Need more information?</h3>
              <p class="mb-4">To learn more about Cooperative Associations in British Columbia, please visit the Cooperative Associations information page on the <a href="https://www2.gov.bc.ca/gov/content/employment-business/business/managing-a-business/permits-licences/businesses-incorporated-companies/cooperative-associations" target="_blank" rel="noopener">BC Government website</a>.</p>
              <a class="link-w-icon" href="https://www2.gov.bc.ca/gov/content/employment-business/business/managing-a-business/permits-licences/news-updates/modernization/coops-services-card"
                 target="_blank" rel="noopener noreferrer">
                <v-icon small class="mr-2">mdi-open-in-new</v-icon>
                <span>Frequently Asked Questions</span>
              </a>
            </v-col>

            <v-col cols="12" md="4">
              <h3 class="mb-6">Contact Us</h3>
              <p class="mb-5">For support or questions about this application, contact us at:</p>
              <ul class="contact-info__list mb-5">
                <li><span>Toll Free:</span> {{ $t('techSupportTollFree') }}</li>
                <li><span>Phone:</span> {{ $t('techSupportPhone') }}</li>
                <li><span>Email:</span> <a href="mailto:bcregistries@gov.bc.ca?subject=BC Registries - Business Registry Support Request">bcregistries@gov.bc.ca</a></li>
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
import { LoginSource, Pages, SessionStorageKeys } from '@/util/constants'
import { Member, MembershipStatus, Organization } from '@/models/Organization'
import { mapActions, mapMutations, mapState } from 'vuex'
import { AccountSettings } from '@/models/account-settings'
import ConfigHelper from '@/util/config-helper'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import LoginBCSC from '@/components/auth/LoginBCSC.vue'
import { User } from '@/models/user'
import { VueConstructor } from 'vue'

@Component({
  name: 'Home',
  components: {
    LoginBCSC
  },
  computed: {
    ...mapState('user', ['userProfile', 'currentUser']),
    ...mapState('org', ['currentAccountSettings', 'currentMembership'])
  },
  methods: {
    ...mapMutations('org', ['resetCurrentOrganisation'])
  }
})

export default class HomeViewOutdated extends Vue {
  private readonly userProfile!: User
  private readonly currentAccountSettings!: AccountSettings
  private readonly currentMembership!: Member
  private readonly getUserProfile!: (identifier: string) => User
  private readonly currentUser!: KCUserProfile
  private noPasscodeDialog = false
  private accountDialog = false
  private oopDialog = false
  private isDirSearchUser: boolean = false
  private isStaffUser: boolean = false
  private readonly resetCurrentOrganisation!: () => void

  private get showManageBusinessesBtn (): boolean {
    return this.currentAccountSettings && this.currentMembership?.membershipStatus === MembershipStatus.Active
  }

  private get showCreateAccountBtn (): boolean {
    return !!this.currentAccountSettings
  }

  private goToManageBusinesses (): void {
    this.$router.push(`/${Pages.MAIN}/${this.currentAccountSettings.id}`)
  }

  private createAccount (): void {
    this.resetCurrentOrganisation()
    this.$router.push(`/${Pages.CREATE_ACCOUNT}`)
  }

  private login () {
    this.$router.push(`/signin/bcsc/${Pages.CREATE_ACCOUNT}`)
  }

  private goToOutOfProvince () {
    this.$router.push(`/${Pages.SETUP_ACCOUNT_NON_BCSC}/${Pages.SETUP_ACCOUNT_NON_BCSC_INSTRUCTIONS}`)
  }

  mounted () {
    this.isDirSearchUser = (this.currentUser?.loginSource === LoginSource.BCROS)
    this.isStaffUser = (this.currentUser?.loginSource === LoginSource.IDIR)
    if (this.isStaffUser) {
      this.$router.push(Pages.STAFF_DASHBOARD)
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";

  .v-alert.covid-alert {
    margin-bottom: 0;
    padding: 0;

    .container {
      padding-top: 2rem;
      padding-bottom: 2rem;
    }
  }

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
    color: #ffffff;
    background-color: $BCgovBlue5;

    h1 {
      margin-bottom: 1.5rem;
      color: inherit;
      letter-spacing: -0.02rem;
      line-height: 1.25;
      font-size: 2.5rem;

      sup {
        top: -0.9rem;
        margin-left: 0.25rem;
        vertical-align: middle;
        color: $BCgovGold5;
        text-transform: uppercase;
        letter-spacing: 0.05rem;
        font-size: .875rem;
      }
    }

    p {
      max-width: 40rem;
      margin-bottom: 2.5rem;
      font-size: 1rem;
    }

    .container {
      padding-top: 3rem;
      padding-bottom: 3.75rem;
    }
  }

  .hero-banner__cta-btns {
    .cta-btn + .cta-btn {
      margin-left: 0.5rem;
    }
  }

  // How to Section
  .how-to-container {
    background: $gray2;

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
      text-align: left;
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
    color: #ffffff;
    background-color: $BCgovBlue5;

    .container {
      padding-top: 2rem;
      padding-bottom: 2.5rem;
    }

    h3 {
      margin-bottom: 1rem;
      padding-bottom: 0.5rem;
      color: inherit;
      border-bottom: 1px solid $BCgovBlue3;
      font-size: 1.25rem;
    }

    a {
      color: $BCgovGold5;
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

  // Fix initial display of the dialog container
  .v-dialog__container {
    display: none;
  }

  a {
    font-weight: 700;
    font-size: 0.875rem;

    .v-icon {
      color: inherit;
    }

    span {
      text-decoration: underline;
    }
  }

  .link-w-icon {
    text-decoration: none;

    span {
      text-decoration: underline;
    }
  }

  .app-footer {
    border-bottom: none !important;
  }

</style>
