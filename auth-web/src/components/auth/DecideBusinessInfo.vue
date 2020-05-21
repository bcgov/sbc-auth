<template>
  <v-container id="decide-business-info-container">
    <v-row>
      <!-- Info Column -->
      <v-col cols="12" md="6">
        <h2>Decide on a Business Type</h2>
        <v-list-item class="list-item" v-for="(item, index) in bulletPoints" :key="index" >
          <v-icon size="6" class="list-item-bullet">mdi-square</v-icon>
          <v-list-item-content>
            <v-list-item-subtitle class="list-item-text">
              {{item.text}}
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
        <!-- Panel Btns -->
        <v-btn large outlined color="#003366" class="btn-learn-more"
          href="https://smallbusinessbc.ca/article/how-to-choose-the-right-business-structure-for-your-small-business/%7D"
          target="_blank" rel="noopener noreferrer">
          Learn More
        </v-btn>
      </v-col>
      <!-- Image Column -->
      <v-col cols="12" md="6">
        <v-img src="../../assets/img/Describe-business-img-Placeholder.png" aspect-ratio="1.2" contain></v-img>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

@Component({})
export default class DecideBusinessInfo extends Vue {
  private bulletPoints: Array<any> = [
    { text: 'Decide which business structure is most appropriate for you: A few options are sole proprietorship, ' +
      'partnership or incorporation.' },
    { text: 'Each structure has a different legal and financial implications.' }
  ]
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  #decide-business-info-container {
    padding-top: 0!important;
    flex-wrap: wrap;

    .list-item {
      margin: .5rem 0;
      padding-left: 0;
    }

    .list-item-bullet {
      color: #CCCCCC;
      margin-right: 1rem;
    }

    .list-item-text {
      white-space: initial;
      color: $gray7;
      font-size: 16px;
      letter-spacing: 0;
      line-height: 24px;
    }

    .btn-learn-more {
      margin-top: .5rem;
      font-weight: bold;
      min-width: 160px;
    }
  }
</style>
