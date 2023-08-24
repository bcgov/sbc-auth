<template>
  <v-container id="decide-business-info-container">
    <v-row>
      <!-- Info Column -->
      <v-col
        cols="12"
        md="6"
      >
        <h2>Decide on a Business Type</h2>
        <v-list-item
          v-for="(item, index) in bulletPoints"
          :key="index"
          class="list-item"
        >
          <v-icon
            size="8"
            class="list-item-bullet mt-5"
          >
            mdi-square
          </v-icon>
          <v-list-item-content>
            <v-list-item-subtitle class="list-item-text">
              {{ item.text }}
              <a
                class="list-item-link"
                :href="item.url"
                target="_blank"
                rel="noopener noreferrer"
              >{{ item.linkText }}
                <v-icon
                  class="link-icon mb-1"
                  small
                  color="#1a5a96"
                >{{ item.icon }}</v-icon>
              </a>
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>

        <!-- Panel Btns -->
        <learn-more-button
          class="mt-3"
          :redirectUrl="learnMoreUrl"
        />
      </v-col>
      <!-- Image Column -->
      <v-col
        cols="12"
        md="6"
      >
        <a
          :href="selectorWizardUrl"
          target="_blank"
        >
          <v-img
            :src="imageSrc"
            aspect-ratio="1.2"
            contain
          />
        </a>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import ConfigHelper from '@/util/config-helper'
import LearnMoreButton from '@/components/auth/common/LearnMoreButton.vue'

@Component({
  components: {
    LearnMoreButton
  }
})
export default class DecideBusinessView extends Vue {
  readonly learnMoreUrl = 'https://smallbusinessbc.ca/article/how-to-choose-the-right-business-structure-for-your-' +
    'small-business/'
  readonly selectorWizardUrl = ConfigHelper.getEntitySelectorUrl()
  readonly bulletPoints: Array<any> = [
    {
      text: `Decide which business structure is most appropriate for you. A few options are: a sole proprietorship,
     partnership, or corporation. Each structure has different legal and financial implications.`
    },
    {
      linkText: 'Use the Business Structures Wizard to help you decide.',
      url: this.selectorWizardUrl,
      icon: `mdi-open-in-new`
    }
  ]
  readonly imageSrc = new URL('@/assets/img/Step1_DecideBusinesswizard_x2.png', import.meta.url).href
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

    .list-item-link {
      font-size: 1rem;
      color: $BCgoveBueText1;
      cursor: pointer;
    }

    .list-item-link:hover {
      color: $BCgoveBueText2;

      .link-icon {
        color: $BCgoveBueText2!important;
      }
    }
  }
</style>
