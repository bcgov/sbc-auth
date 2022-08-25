<template>
  <v-container id="maintain-info-container">
    <v-row>
      <!-- Info Column -->
      <v-col cols="12" md="6">
        <h2>Manage and Maintain Your Business</h2>
        <v-list class="py-0 my-4" color="transparent">
          <v-list-item class="list-item" v-for="(item, index) in bulletPoints" :key="index">
            <v-icon size="8" class="list-item-bullet mt-5">mdi-square</v-icon>
            <v-list-item-content>
              <v-list-item-subtitle class="list-item-text">
                {{item.text}}
              </v-list-item-subtitle>
              <v-list-item class="list-item list-item-sub" v-for="(item, index) in item.subText" :key="`sub-${index}`">
                <v-icon size="8" class="list-item-bullet mt-5">mdi-square</v-icon>
                <v-list-item-content>
                  <v-list-item-subtitle class="list-item-text">
                    {{item.text}}
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list-item-content>
          </v-list-item>
        </v-list>
        <!-- Panel Btns -->
        <div class="incorporate-btns">
          <v-btn large color="bcgovblue" class="cta-btn font-weight-bold mr-2 white--text business-btn"
            @click="emitRedirectManage()">
            Manage my Business
          </v-btn>
          <LearnMoreButton isWide=true :redirect-url="learnMoreUrl"/>
          <div class="d-flex mt-8">
            <span class="body-1">New to BC Registries?</span>
            <router-link class="ml-2 body-1 font-weight-bold"
              to="/choose-authentication-method"
            >Create a BC Registries Account
            </router-link>
          </div>
          <p v-if="!userProfile" class="mt-5">
            <v-menu top offset-y v-model="contactUsPopover" :close-on-content-click="false" attach="#maintain-info-container">
              <v-card class="contact-popover">
                <v-list class="pa-5" max-width="30rem">
                  <v-list-item class="pb-3">
                    <v-list-item-title class="popover-title mt-5 font-weight-bold">
                      Don't have a Passcode for your Cooperative<br>Association?
                    </v-list-item-title>
                    <v-list-item-action class="mt-0">
                      <v-icon @click="contactUsPopover = false" color="bcgovblueLink">mdi-close</v-icon>
                    </v-list-item-action>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>
                        If you have not received your Access Letter from BC Registries,<br>
                        or have lost your Passcode, please contact us at:
                      </v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>
                        {{ $t('labelTollFree') }}
                        <a :href="`tel:+${$t('maximusSupportTollFree')}`">{{ $t('maximusSupportTollFree') }}</a>
                      </v-list-item-subtitle>
                      <v-list-item-subtitle class="my-1">
                        {{ $t('labelVictoriaOffice') }}
                        <a :href="`tel:+${$t('maximusSupportPhone')}`">{{ $t('maximusSupportPhone') }}</a>
                      </v-list-item-subtitle>
                      <v-list-item-subtitle>
                        {{ $t('labelEmail') }}
                        <a :href="'mailto:' + $t('maximusSupportEmail') + '?subject=' + $t('maximusSupportEmailSubject')">{{ $t('maximusSupportEmail') }}</a>
                      </v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle class="font-weight-bold">{{ $t('labelHoursOfOperation') }}</v-list-item-subtitle>
                      <v-list-item-subtitle class="my-1">{{ $t('hoursOfOperation') }}</v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>
                        <a :href="faqUrl" rel="noopener noreferrer" target="_blank">
                          Frequently Asked Questions
                        </a>
                      </v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                </v-list>
              </v-card>
            </v-menu>
          </p>
        </div>
      </v-col>
      <!-- Image Column -->
      <v-col cols="12" md="6">
        <a :href="learnMoreUrl" target="_blank">
          <v-img src="../../../assets/img/Step4_Maintain_x2.png" aspect-ratio="1.2" contain></v-img>
        </a>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import ConfigHelper from '@/util/config-helper'
import LearnMoreButton from '@/components/auth/common/LearnMoreButton.vue'
import { User } from '@/models/user'
import { appendAccountId } from 'sbc-common-components/src/util/common-util'

@Component({
  components: {
    LearnMoreButton
  }
})
export default class MaintainBusinessView extends Vue {
  private contactUsPopover = false
  private readonly faqUrl = 'https://www2.gov.bc.ca/gov/content/employment-business/business/managing-a-business/permits-licences/news-updates/modernization/coops-services-card'
  protected readonly learnMoreUrl = 'https://www2.gov.bc.ca/gov/content/governments/organizational-structure/ministries-organizations/ministries/citizens-services/bc-registries-online-services'

  private readonly bulletPoints: Array<any> = [
    { text: 'Once your business is incorporated or registered you are required to keep information about your business up to date with the Registry.' },
    { text: 'By managing your business through your BC Registry account you can:',
      subText: [
        { text: 'See which Annual Reports are due for your corporation and file each year.' },
        { text: 'View and change your current directors or owners and addresses.' },
        { text: 'See the history of your business\' filings and download copies of all documents including your Statement of Registration, Certificate of Incorporation and more.' }
      ]
    }
  ]

  @Prop()
  private userProfile: User

  private emitRedirectManage () {
    if (this.userProfile) {
      this.emitManageBusinesses()
    } else {
      window.location.assign(appendAccountId(`${ConfigHelper.getRegistryHomeURL()}dashboard`))
    }
  }

  @Emit('login')
  private emitLogin () {}

  @Emit('account-dialog')
  private emitAccountDialog () {}

  @Emit('manage-businesses')
  private emitManageBusinesses () {}
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  #maintain-info-container {
    padding-top: 0 !important;
    flex-wrap: wrap;

    .list-item {
      align-items: flex-start;
      padding-left: 0;
    }

    .list-item-text + .list-item {
      margin-top: 1rem;
    }

    .list-item-sub {
      padding-left: 1.5rem;
    }

    .list-item-bullet {
      color: $BCgovBullet;
      margin-right: 1rem;
    }

    .list-item-text {
      white-space: initial;
      color: $gray7;
      font-size: 1rem;
      letter-spacing: 0;
      line-height: 1.5rem;
    }

    .maintain-info-btns {
      display: flex;
      flex-direction: column;

      .v-btn {
        max-width: 250px;
        font-weight: bold;
        color: $BCgovBlue5;
      }

      .v-btn:hover {
        opacity: .8;
      }
    }

    .contact-popover {
      .v-list-item-title {
        font-size: .875rem;
      }

      .v-list-item__subtitle {
        font-size: .75rem;
      }
    }

    .business-btn:hover {
      color: white !important;
      opacity: .8;
    }
  }
</style>
