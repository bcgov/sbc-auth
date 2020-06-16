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
          <h1>Start a Benefit Company and <br> Keep Cooperatives Records up to date</h1>
          <p class="my-10">The Business Registry manages the creation (incorporation and registration) <br> and listing of businesses
            and organizations in British Columbia.</p>
          <div class="hero-banner__cta-btns">
            <!-- Authenticated -->
            <div v-if="userProfile" class="cta-btns-authenticated">
              <v-btn large color="#003366" class="cta-btn white--text"
                     :href="nroUrl" target="_blank" rel="noopener noreferrer">
                Request a Name
              </v-btn>
              <v-btn large color="#003366" class="cta-btn white--text"
                     @click="goToManageBusinesses()">
                Incorporate a Named Benefit Company
              </v-btn>
              <v-btn large color="#003366" class="cta-btn white--text"
                     @click="goToManageBusinesses(true)">
                Incorporate a Numbered Benefit Company
              </v-btn>
              <v-btn large color="#fcba19" class="cta-btn"
                     @click="goToManageBusinesses()">
                Manage an Existing Business
              </v-btn>
            </div>
            <!-- Non-authenticated -->
            <div v-else>
              <v-btn large color="#fcba19" class="cta-btn"
                     @click="login()">
                Log in with BC Services Card
              </v-btn>
              <v-btn large color="#003366" class="cta-btn ml-4 white--text"
                    :href="nroUrl" target="_blank" rel="noopener noreferrer">
                Request a Name
              </v-btn>
              <p class="mt-10">New to BC Registries? <a @click="accountDialog = true" class="create-account-link">
                <u>Create a BC Registries Account</u></a>
              </p>
            </div>
          </div>

          <v-dialog v-model="accountDialog" max-width="640">
            <LoginBCSC>
              <template v-slot:actions>
                <v-btn large color="primary" @click="login()">Log in</v-btn>
                <v-btn large depressed color="default" @click="accountDialog = false">Cancel</v-btn>
              </template>
            </LoginBCSC>
          </v-dialog>
        </v-container>
      </header>
      <div class="how-to-container mt-10">
        <v-container>
          <h2>How does it work?</h2>
          <InfoStepper />
          <transition name="slide-x-transition">
            <router-view
              :userProfile="userProfile"
              @login="login()"
              @account-dialog="accountDialog = true"
              @manage-businesses="goToManageBusinesses($event)"/>
          </transition>
        </v-container>
      </div>
      <TestimonialQuotes />
      <BcscPanel
        :userProfile="userProfile"
        @login="login()"
        @account-dialog="accountDialog = true"
      />
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
import { LoginSource, Pages, SessionStorageKeys } from '@/util/constants'
import { Member, MembershipStatus } from '@/models/Organization'
import { mapMutations, mapState } from 'vuex'
import { AccountSettings } from '@/models/account-settings'
import BcscPanel from '@/components/auth/BcscPanel.vue'
import ConfigHelper from '@/util/config-helper'
import InfoStepper from '@/components/auth/stepper/InfoStepper.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import LoginBCSC from '@/components/auth/LoginBCSC.vue'
import TestimonialQuotes from '@/components/auth/TestimonialQuotes.vue'
import { User } from '@/models/user'

@Component({
  name: 'Home',
  components: {
    BcscPanel,
    InfoStepper,
    LoginBCSC,
    TestimonialQuotes
  },
  computed: {
    ...mapState('user', ['userProfile', 'currentUser']),
    ...mapState('org', ['currentAccountSettings', 'currentMembership'])
  },
  methods: {
    ...mapMutations('org', ['resetCurrentOrganisation'])
  }
})
export default class HomeViewDev extends Vue {
  private readonly userProfile!: User
  private readonly currentAccountSettings!: AccountSettings
  private readonly currentMembership!: Member
  private readonly getUserProfile!: (identifier: string) => User
  private readonly currentUser!: KCUserProfile
  private noPasscodeDialog = false
  private accountDialog = false
  private isDirSearchUser: boolean = false
  private readonly resetCurrentOrganisation!: () => void
  private nroUrl = ConfigHelper.getNroUrl()

  private get showManageBusinessesBtn (): boolean {
    return this.currentAccountSettings && this.currentMembership?.membershipStatus === MembershipStatus.Active
  }

  private get showCreateAccountBtn (): boolean {
    return !!this.currentAccountSettings
  }

  private goToManageBusinesses (isNumberedCompanyRequest: boolean = false): void {
    let manageBusinessUrl: any = { path: `/${Pages.MAIN}/${this.currentAccountSettings.id}` }
    if (isNumberedCompanyRequest) manageBusinessUrl.query = { isNumberedCompanyRequest }

    this.$router.push(manageBusinessUrl)
  }

  private createAccount (): void {
    this.resetCurrentOrganisation()
    this.$router.push(`/${Pages.CREATE_ACCOUNT}`)
  }

  private login () {
    this.$router.push(`/signin/bcsc/${Pages.CREATE_ACCOUNT}`)
  }

  mounted () {
    this.isDirSearchUser = (this.currentUser?.loginSource === LoginSource.BCROS)
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
    color: $gray9;
    background-color: #ffffff;

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
      margin: 1.5rem 0;
      font-size: 1rem;
    }

    .container {
      padding-top: 3rem;
      padding-bottom: 3.75rem;
      background-image: url('../../assets/img/hero-img-min.jpg');
      background-position:  bottom right;
      background-size: 90% 105%;
      background-repeat: no-repeat;
      box-shadow: -10px 0 10px 0 #ffffff inset;
    }
  }

  @media only screen and (max-width: 640px) {
    .hero-banner {
      background-image: none;
    }
  }
  @media only screen and (min-width: 1920px) {
    .hero-banner {
      background-size: 1920px 110%;
    }
  }

  .hero-banner__cta-btns {
    display: flex;
    min-height: 150px;

    .cta-btn {
      flex: 0 0 100%;
    }

    .cta-btns-authenticated, .cta-btns-authenticated > div {
      display: flex;
      max-width: 350px;
      flex-wrap: wrap;
      margin-bottom: 13px;

      .cta-btn {
        flex: 0 0 100%;
        margin-bottom: 13px;
      }
    }

    .create-account-link {
      font-size: 1rem;
      color: $BCgoveBueText1 !important;

      :hover {
        color: $BCgoveBueText2 !important;
      }
    }
  }

  // How to Section
  .how-to-container {
    background: $BCgovBG;
    width: 100%;

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
