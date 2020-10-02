<template>
  <v-container id="decide-business-info-container">
    <v-row>
      <!-- Info Column -->
      <v-col cols="12" md="6">
        <h2>Decide on a Business Type</h2>
        <v-list-item class="list-item" v-for="(item, index) in bulletPoints" :key="index" >
          <v-icon size="8" class="list-item-bullet mt-5">mdi-square</v-icon>
          <v-list-item-content>
            <v-list-item-subtitle class="list-item-text">
              {{item.text}}
              <a href="https://www2.gov.bc.ca/gov/content/employment-business/business/bc-companies/benefit-company"
               class="learn-more-link" target="_blank" rel="noopener noreferrer">
                {{item.linkText}}
              </a>
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
        <!-- Panel Btns -->
        <learn-more-button
          :redirectUrl="learnMoreUrl"
        />
      </v-col>
      <!-- Image Column -->
      <v-col cols="12" md="6">
        <a :href="learnMoreUrl" target="_blank">
          <v-img src="../../../assets/img/Step1_DecideBusiness_x2.png" aspect-ratio="1.2" contain></v-img>
        </a>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import LearnMoreButton from '@/components/auth/common/LearnMoreButton.vue'

@Component({
  components: {
    LearnMoreButton
  }
})
export default class DecideBusinessView extends Vue {
  private readonly learnMoreUrl = 'https://smallbusinessbc.ca/article/how-to-choose-the-right-business-structure-for-your-' +
    'small-business/'
  private readonly bulletPoints: Array<any> = [
    { text: 'Decide which business structure is most appropriate for you: A few options are sole proprietorship, ' +
      'partnership or incorporation.' },
    { text: 'Each structure has a different legal and financial implications.',
      linkText: 'Make sure a Benefit Company is right for you.'
    }
  ]
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  #decide-business-info-container {
    padding-top: 0 !important;
    flex-wrap: wrap;

    .v-btn:hover {
      opacity: .8;
    }

    .list-item {
      align-items: flex-start;
      margin: .5rem 0;
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

    .learn-more-link {
      font-size: 1rem;
      color: $BCgoveBueText1;
    }

    .learn-more-link:hover {
      color: $BCgoveBueText2;
    }
  }
</style>
