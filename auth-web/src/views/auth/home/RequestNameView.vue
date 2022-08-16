<template>
  <v-container id="request-name-info-container">
    <v-row>
      <!-- Info Column -->
      <v-col cols="12" md="6">
        <h2>Request a Name or Use a Numbered Company</h2>
        <v-list-item class="list-item" v-for="(item, index) in bulletPoints" :key="index" >
          <v-icon size="8" class="list-item-bullet mt-5">mdi-square</v-icon>
          <v-list-item-content>
            <v-list-item-subtitle class="list-item-text">
              {{item.text}}
            </v-list-item-subtitle>
            <div v-if="index=== 1">
              <v-list-item class="list-item" v-for="(subItem, subIndex) in subBulletPoints" :key="subIndex">
                <v-icon size="8" class="list-item-bullet mt-5">mdi-square</v-icon>
                <v-list-item-content>
                  <v-list-item-subtitle class="list-item-text">
                    {{ subItem.text }}
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </div>
          </v-list-item-content>
        </v-list-item>
        <v-list-item class="list-item">
          <v-icon size="8" class="list-item-bullet mt-5">mdi-square</v-icon>
          <v-list-item-content>
            <v-list-item-subtitle class="list-item-text">
              You can choose to incorporate a <numbered-company-tooltip />
              and start your incorporation immediately.
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
        <!-- Panel Btns -->
        <div class="request-name-info-btns mt-5">
          <NameRequestButton class="mr-2" :isInverse="true"/>
          <LearnMoreButton :redirect-url="learnMoreUrl"/>
        </div>
        <p class="mt-5">
          Have an existing Name Request?
          <a class="status-link" @click="goToNameRequestExisting()">
            Check your Name Request Status
          </a>
        </p>
      </v-col>
      <!-- Image Column -->
      <v-col cols="12" md="6">
        <v-img
          src="../../../assets/img/Step2_NameRequest_x2.png"
          aspect-ratio="1.2"
          contain
          class="cursor-pointer"
          @click="goToNameRequest()"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import ConfigHelper from '@/util/config-helper'
import { LDFlags } from '@/util/constants'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import LearnMoreButton from '@/components/auth/common/LearnMoreButton.vue'
import NameRequestButton from '@/components/auth/home/NameRequestButton.vue'
import NumberedCompanyTooltip from '@/components/auth/common/NumberedCompanyTooltip.vue'
import { appendAccountId } from 'sbc-common-components/src/util/common-util'

@Component({
  components: {
    NameRequestButton,
    LearnMoreButton,
    NumberedCompanyTooltip
  }
})
export default class RequestNameView extends Vue {
  private readonly learnMoreUrl = 'https://www2.gov.bc.ca/gov/content/employment-business/business/managing-a-business/permits-licences/businesses-incorporated-companies/approval-business-name'
  private bulletPoints: Array<any> = [
    { text: 'You can choose to have a name or use the incorporation number as the name of the business.' },
    { text: 'If you choose to have a name for your business, create a unique name that ensures the public is not confused or mislead by similar corporate names.' }
  ]
  private subBulletPoints: Array<any> = [
    { text: 'Submit your name choices for examniation by the Business Registry.' },
    { text: 'If your name is approved, you can use it to register or incorporate your business.' }
  ]

  // open Name Request in current tab to retain current account and user
  goToNameRequestExisting (): void {
    if (LaunchDarklyService.getFlag(LDFlags.LinkToNewNameRequestApp)) {
      window.location.href = appendAccountId(`${ConfigHelper.getNameRequestUrl()}existing`)
    } else {
      window.location.href = appendAccountId(`${ConfigHelper.getNroUrl()}nro.htm?_flowId=anonymous-monitor-flow&_flowExecutionKey=e1s1`)
    }
  }

  // open Name Request in current tab to retain current account and user
  goToNameRequest (): void {
    if (LaunchDarklyService.getFlag(LDFlags.LinkToNewNameRequestApp)) {
      window.location.href = appendAccountId(ConfigHelper.getNameRequestUrl())
    } else {
      window.location.href = appendAccountId(ConfigHelper.getNroUrl())
    }
  }
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  #request-name-info-container {
    padding-top: 0 !important;
    flex-wrap: wrap;

    .list-item {
      align-items: flex-start;
      margin: .5rem 0;
      padding-left: 0;
    }

    .list-item .list-item:last-child {
      margin-bottom: 0;
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

    .request-name-info-btns {
      display: flex;

      .v-btn {
        font-weight: bold;
        width: 160px;
      }

      .v-btn:hover {
        opacity: .8;
      }
    }

    .status-link {
      font-size: 1rem;
      color: $BCgoveBueText1;
      text-decoration: underline;
    }

    .status-link:hover {
      color: $BCgoveBueText2;
    }
  }
</style>
