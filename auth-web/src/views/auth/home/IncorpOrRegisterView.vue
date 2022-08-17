<template>
  <v-container id="incorporate-info-container">
    <v-row>
      <!-- Info Column -->
      <v-col cols="12" md="6">
        <h2>Incorporate or Register</h2>
        <v-list class="py-0 mt-4 mb-6" color="transparent">
          <v-list-item class="list-item">
            <v-icon size="8" class="list-item-bullet mt-5">mdi-square</v-icon>
            <v-list-item-content>
              <v-list-item-subtitle class="list-item-text">
                If you have an approved Name Request (NR number), or you want a <numbered-company-tooltip />,
                you can start your Incorporation Application.
              </v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
          <v-list-item class="list-item" v-for="(item, index) in bulletPoints" :key="index">
            <v-icon size="8" class="list-item-bullet mt-5">mdi-square</v-icon>
            <v-list-item-content>
              <v-list-item-subtitle class="list-item-text">
                {{item.text}}
              </v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </v-list>
        <!-- Panel Btns -->
        <template>
          <v-btn large color="bcgovblue" class="cta-btn font-weight-bold mr-2 white--text registry-btn"
            @click="emitRedirectManage()">
            Go to My Business Registry
          </v-btn>
        </template>
        <LearnMoreButton isWide=true :redirect-url="learnMoreUrl"/>
        <div class="d-flex mt-8">
          <span class="body-1">New to BC Registries?</span>
          <router-link class="ml-2 body-1 font-weight-bold"
            to="/choose-authentication-method"
          >Create a BC Registries Account
          </router-link>
        </div>
      </v-col>
      <!-- Image Column -->
      <v-col cols="12" md="6">
        <a :href="learnMoreUrl" target="_blank">
          <v-img src="../../../assets/img/Step3_Incorporate_x2.png" aspect-ratio="1.2" contain></v-img>
        </a>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import ConfigHelper from '@/util/config-helper'
import LearnMoreButton from '@/components/auth/common/LearnMoreButton.vue'
import NumberedCompanyTooltip from '@/components/auth/common/NumberedCompanyTooltip.vue'
import { User } from '@/models/user'
import { appendAccountId } from 'sbc-common-components/src/util/common-util'

@Component({
  components: {
    LearnMoreButton,
    NumberedCompanyTooltip
  }
})
export default class IncorpOrRegisterView extends Vue {
  protected readonly learnMoreUrl = 'https://www2.gov.bc.ca/gov/content/governments/organizational-structure/ministries-organizations/ministries/citizens-services/bc-registries-online-services'
  private readonly bulletPoints: Array<any> = [
    { text: 'For Named Companies, add your existing Name Request number to your account and open it.' },
    { text: 'Establish your company\'s articles and prepare an Incorporation Agreement. Either create your own, or use template provided in the Incorporation Application.' },
    { text: 'Complete the Incorporation Application by providing information about your company: addresses, directors and share structure.' },
    { text: 'Retain a copy of all Incorporation documents for your business\'s records.' }
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
  private emitManageBusinesses (isNumberedCompanyRequest: boolean = false) {
    return isNumberedCompanyRequest
  }
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  #incorporate-info-container {
    padding-top: 0 !important;
    flex-wrap: wrap;

    a:hover {
      color: $BCgoveBueText2;
    }

    .list-item {
      align-items: flex-start;
      padding-left: 0;
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

    .v-btn:hover {
      opacity: .8;
    }

    .incorporate-btns {
      flex-direction: column;

      .incorporate-btn {
        align-self: flex-start;
      }
    }

    .registry-btn:hover {
      color: white !important;
      opacity: .8;
    }
  }
</style>
