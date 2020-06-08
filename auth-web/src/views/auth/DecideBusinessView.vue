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
              <a href="https://smallbusinessbc.ca/article/how-to-choose-the-right-business-structure-for-your-small-business/%7D"
               class="learn-more-link" target="_blank" rel="noopener noreferrer">
                {{item.linkText}}
              </a>
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
        <!-- Panel Btns -->
        <LearnMoreButton />
      </v-col>
      <!-- Image Column -->
      <v-col cols="12" md="6">
        <v-img src="../../assets/img/Step1_DecideBusiness_x1.jpg" aspect-ratio="1.2" contain></v-img>
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
  private bulletPoints: Array<any> = [
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
    padding-top: 0!important;
    flex-wrap: wrap;

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
      color: $BCgoveBueText1!important;
    }

    .learn-more-link:hover {
      color: $BCgoveBueText2!important;
    }
  }
</style>
