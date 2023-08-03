<template>
  <div id="help-resolution" class="mb-12">
    <div class="ma-6">
      <div class="help-btn top" @click="helpToggle = !helpToggle">
        <v-icon color="primary">mdi-help-circle-outline</v-icon>
        <span v-if="!helpToggle" class="pl-2">{{ helpContent.toggleHelpShow }}</span>
        <span v-else class="pl-2">{{ helpContent.toggleHelpHide }}</span>
      </div>
      <v-expand-transition v-if="helpToggle">
        <section class="help-section info-text">
          <header class="help-header mt-4">
            <p class="title-text mt-4">{{ helpContent.title }}</p>
          </header>
          <br>
          <div class="help-text mt-4">
            <p>{{ helpContent.intro }}</p>
            <ol>
                <li class="mt-12" v-for="(step, index) in helpContent.steps" :key="index">
                    <strong>{{ step.title }}</strong>
                    <ul class="mt-8">
                    <li v-for="(item, i) in step.items" :key="i">
                        <p v-if="typeof item === 'string'">{{ item }}</p>
                        <p v-else v-html="item.content"></p>
                    </li>
                    </ul>
                </li>
            </ol>
          </div>
          <div class="help-btn bottom" @click="helpToggle = !helpToggle">{{ helpContent.toggleHelpHide }}</div>
        </section>
      </v-expand-transition>
    </div>
  </div>
</template>

<script lang="ts">
import helpContent from '../../../resources/helpContent.json'
import { ref } from '@vue/composition-api'

export default {
  setup () {
    const helpToggle = ref(false)
    return { helpToggle, helpContent }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

#sr-heading {
  color: $gray9
}

.help-btn {
  cursor: pointer;
  color: $app-blue;
  vertical-align: middle;
}

.v-icon {
  margin-top: -3px;
}

.help-section {
  border-top: 1px dashed $gray6;
  border-bottom: 1px dashed $gray6;
  margin: 1.5rem 0;
  padding: 1rem 0;
}

.help-header {
  display: flex;
  justify-content: center;
}

.help-btn.bottom {
  font-size: $px-13;
  text-decoration: underline;
  display: flex;
  direction: rtl;
}

.title-text {
  color: #1669bb;
}

.help-text {
  margin-left: 80px;
  margin-right: 80px;
}

</style>
