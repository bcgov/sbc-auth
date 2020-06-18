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
        <!-- Authenticated -->
        <template v-if="userProfile">
          <div class="incorporate-btns d-flex flex-column">
            <v-btn large dark color="bcgovblue" class="incorporate-btn font-weight-bold mb-7"
              @click="emitManageBusinesses()">
              Incorporate a Named Benefit Company
            </v-btn>
            <v-btn large dark color="bcgovblue" class="incorporate-btn font-weight-bold mb-7"
              @click="emitManageBusinesses(true)">
              Incorporate a Numbered Benefit Company
            </v-btn>
          </div>
        </template>
        <!-- Not Authenticated -->
        <template v-else>
          <v-btn large color="bcgovgold" class="cta-btn font-weight-bold mr-2" to="/choose-authentication-method">
            Create a BC Registries account
          </v-btn>
        </template>
        <learn-more-button
        :redirect-url="learnMoreUrl"/>
      </v-col>
      <!-- Image Column -->
      <v-col cols="12" md="6">
        <a :href="learnMoreUrl" target="_blank">
          <v-img src="../../assets/img/Step3_Incorporate_x2.png" aspect-ratio="1.2" contain></v-img>
        </a>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import LearnMoreButton from '@/components/auth/common/LearnMoreButton.vue'
import NumberedCompanyTooltip from '@/components/auth/common/NumberedCompanyTooltip.vue'
import { Pages } from '@/util/constants'
import { User } from '@/models/user'

@Component({
  components: {
    LearnMoreButton,
    NumberedCompanyTooltip
  }
})
export default class IncorpOrRegisterView extends Vue {
  private readonly learnMoreUrl = 'https://smallbusinessbc.ca/article/how-to-choose-the-right-business-structure-for-your-small-business/'
  private readonly bulletPoints: Array<any> = [
    { text: 'For Named Companies, add your existing Name Request number to your account and open it.' },
    { text: 'Establish your company\'s articles and prepare an Incorporation Agreement. Either create your own, or use template provided in the Incorporation Application.' },
    { text: 'Complete the Incorporation Application by providing information about your company: addresses, directors and share structure.' },
    { text: 'Retain a copy of all Incorporation documents for your business\'s records.' }
  ]

  @Prop()
  private userProfile: User

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
  }
</style>
