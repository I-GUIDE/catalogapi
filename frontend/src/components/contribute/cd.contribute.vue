<template>
  <v-container class="cd-contribute">
    <div class="text-h4">Contribute</div>
    <v-divider class="mt-4 mb-12"></v-divider>
    <cz-form
      :schema="schema"
      :uischema="uischema"
      :schemaDefaults="schemaDefaults"
      :isReadOnly="isReadonly"
      :errors.sync="errors"
      @update:data="onDataChange"
      ref="form"
    />

    <div
      class="d-flex form-controls flex-column flex-sm-row flex-grow-1 flex-sm-grow-0 gap-1"
    >
      <v-spacer></v-spacer>
      <v-btn @click="onCancel">Cancel</v-btn>
      <v-menu :disabled="!errors.length" open-on-hover bottom left offset-y>
        <template v-slot:activator="{ on, attrs }">
          <div
            v-bind="attrs"
            v-on="on"
            class="d-flex form-controls flex-column flex-sm-row"
          >
            <v-badge
              :value="!!errors.length"
              bordered
              color="error"
              icon="mdi-exclamation-thick"
              overlap
            >
              <v-btn
                color="primary"
                depressed
                @click="submit"
                :disabled="
                  isSaving ||
                  isReadonly ||
                  !!errors.length ||
                  !hasUnsavedChanges
                "
                >Submit</v-btn
              >
            </v-badge>
          </div>
        </template>

        <div class="white pa-4">
          <ul
            v-for="(error, index) of errors"
            :key="index"
            class="text-subtitle-1"
          >
            <li>
              <b>{{ error.title }}</b> {{ error.message }}.
            </li>
          </ul>
        </div>
      </v-menu>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { Notifications, CzForm } from "@cznethub/cznet-vue-core";

import User from "@/models/user.model";

// const schema = require("@/schemas/schema.json");
const uischema = require("@/schemas/uischema.json");
const schemaDefaults = require("@/schemas/uischema.json");

@Component({
  name: "cd-contribute",
  components: { CzForm },
})
export default class CdContribute extends Vue {
  // protected schema = null;
  protected uischema = null;
  protected schemaDefaults = null;
  protected isReadonly = false;
  protected errors = [];
  protected data = {};
  protected timesChanged = 0;
  protected isSaving = false;

  // beforeCreate() {
  //   this.schema = schema;
  //   this.uischema = uischema;
  //   this.schemaDefaults = schemaDefaults;
  // }

  protected get schema() {
    return User.$state.schema;
  }

  protected get hasUnsavedChanges(): boolean {
    return User.$state.hasUnsavedChanges;
  }

  protected set hasUnsavedChanges(value: boolean) {
    User.commit((state) => {
      state.hasUnsavedChanges = value;
    });
  }

  created() {
    this.hasUnsavedChanges = false;
  }

  protected async submit() {
    try {
      this.isSaving = true;
      const wasSaved = await User.submit(this.data);
      this.isSaving = false;
      if (wasSaved) {
        this.hasUnsavedChanges = false;
        Notifications.toast({
          message: `Your submission has been saved!`,
          type: "success",
        });
        this.$router.push({ name: "home" });
      } else {
        // Failed to save
        Notifications.toast({
          message: `Failed to save submission`,
          type: "error",
        });
      }
    } catch (e) {
      this.isSaving = false;
    }
  }

  protected onCancel() {
    this.$router.push({ name: "home" });
  }

  protected onDataChange(data) {
    this.data = data;

    // Pristine/dirty checks are currently not supported in jsonforms.
    // We use onChange event for now by ignoring the two times it is called when the form is rendered.
    // https://spectrum.chat/jsonforms/general/pristine-and-dirty-checking~2ece93ab-7783-41cb-8ba1-804414eb1da4?m=MTU2MzM0OTY0NDQxNg==

    // json-forms emits 'change' event 3 times during instantioation.
    const changesDuringInstantiation = 3;

    if (this.timesChanged <= changesDuringInstantiation) {
      this.timesChanged = this.timesChanged + 1;
    }

    this.hasUnsavedChanges = this.timesChanged > changesDuringInstantiation;
  }

  // mounted() {
  //   Notifications.toast({
  //     message: `Failed to perform search`,
  //     type: "error",
  //   });

  //   Notifications.openDialog({
  //     title: "some title",
  //     content: "some content",
  //     onConfirm: () => {},
  //   });
  // }
}
</script>

<style lang="scss" scoped></style>