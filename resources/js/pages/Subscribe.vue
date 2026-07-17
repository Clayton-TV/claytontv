<script setup lang="ts">
import { Button } from '@/ui/button';
import { Input } from '@/ui/input';
import { Head } from '@inertiajs/vue3';
import { Mail } from 'lucide-vue-next';
import { ref } from 'vue';

const FORM_ACTION = 'https://clayton.us2.list-manage.com/subscribe/post?u=d5c4aef36a582de40d5837112&id=8fc2472183&f_id=006179e0f0';
const PRIVACY_URL = 'https://clayton.tv/Clayton_TV_Data_Privacy_Notice.pdf';

const email = ref('');
const firstName = ref('');
const lastName = ref('');
const error = ref('');
const formRef = ref<HTMLFormElement | null>(null);

function isValidEmail(value: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
}

function handleSubmit() {
    if (!isValidEmail(email.value)) {
        error.value = 'Please enter a valid email address.';
        return;
    }
    error.value = '';

    // @TODO: remove the following debugging log and submit to Mailchimp
    const formData = new FormData(formRef.value!);
    const payload = Object.fromEntries(formData.entries());
    console.log('Mailchimp payload:', payload);
    // formRef.value?.submit();
}
function clearErrorIfValid(event: Event) {
    const value = (event.target as HTMLInputElement).value;
    if (error.value && isValidEmail(value)) {
        error.value = '';
    }
}
</script>

<template>
    <div>
        <Head title="Subscribe" />
        <div class="mx-auto max-w-2xl px-4 py-14 lg:px-8">
            <div class="flex items-start gap-3">
                <span class="bg-primary/10 text-primary flex h-10 w-10 flex-none items-center justify-center rounded-full" aria-hidden="true">
                    <Mail class="h-5 w-5" />
                </span>
                <div class="min-w-0">
                    <h1 class="font-display text-foreground text-2xl font-bold sm:text-3xl">Subscribe</h1>
                </div>
            </div>

            <p class="text-muted-foreground mt-6 leading-relaxed">
                At Clayton.TV we strive to bring Christ-centred, biblical videos into one place with fresh content weekly. Our aim is to support and
                equip Christians around the world. If you find our work helpful, and would like regular email updates from Clayton.TV, please opt-in
                below (you can opt out at any time).
            </p>

            <form ref="formRef" :action="FORM_ACTION" method="post" target="_blank" novalidate class="mt-8 space-y-5" @submit.prevent="handleSubmit">
                <p class="text-muted-foreground text-sm"><span class="text-destructive">*</span> indicates required</p>

                <!-- Email (required) -->
                <div>
                    <label for="mce-EMAIL" class="text-foreground mb-1.5 block text-sm font-medium">
                        Email Address <span class="text-destructive">*</span>
                    </label>
                    <Input
                        id="mce-EMAIL"
                        v-model="email"
                        type="email"
                        name="EMAIL"
                        required
                        autocomplete="email"
                        placeholder="you@example.com"
                        :class="{ 'border-destructive': error }"
                        @input="clearErrorIfValid"
                    />
                    <p v-if="error" class="text-destructive mt-1.5 text-sm" role="alert">
                        {{ error }}
                    </p>
                </div>

                <!-- Name fields -->
                <div class="grid gap-4 sm:grid-cols-2">
                    <div>
                        <label for="mce-FNAME" class="text-foreground mb-1.5 block text-sm font-medium">First Name</label>
                        <Input id="mce-FNAME" v-model="firstName" type="text" name="FNAME" autocomplete="given-name" />
                    </div>
                    <div>
                        <label for="mce-LNAME" class="text-foreground mb-1.5 block text-sm font-medium">Last Name</label>
                        <Input id="mce-LNAME" v-model="lastName" type="text" name="LNAME" autocomplete="family-name" />
                    </div>
                </div>

                <!-- GDPR / Marketing permissions -->
                <fieldset class="border-border space-y-3 border-t pt-5">
                    <legend class="text-foreground text-sm font-medium">Marketing Permissions</legend>
                    <p class="text-muted-foreground text-sm leading-relaxed">
                        Clayton TV will use the information you provide on this form to be in touch with you with regular email updates. Please
                        confirm you would like to hear from us:
                    </p>
                    <div class="flex items-center gap-2">
                        <input id="gdpr_669" type="checkbox" name="gdpr[669]" value="Y" class="accent-primary h-4 w-4" />
                        <label for="gdpr_669" class="text-foreground text-sm">Email</label>
                    </div>
                    <p class="text-muted-foreground text-xs leading-relaxed">
                        You can change your mind at any time by clicking the unsubscribe link in the footer of any email you receive from us, or by
                        contacting us at
                        <a href="mailto:enquiries@clayton.tv" class="text-primary underline-offset-4 hover:underline">enquiries@clayton.tv</a>. We
                        will treat your information with respect. For more information about our privacy practices please see our
                        <a :href="PRIVACY_URL" target="_blank" rel="noopener" class="text-primary underline-offset-4 hover:underline"
                            >privacy notice</a
                        >.
                    </p>
                </fieldset>

                <p class="text-muted-foreground text-xs leading-relaxed">
                    We use Mailchimp as our marketing platform. By clicking below to subscribe, you acknowledge that your information will be
                    transferred to Mailchimp for processing.
                    <a href="https://mailchimp.com/legal/terms" target="_blank" rel="noopener" class="text-primary underline-offset-4 hover:underline"
                        >Learn more</a
                    >
                    about Mailchimp's privacy practices.
                </p>

                <!-- Honeypot anti-bot field -->
                <div aria-hidden="true" class="absolute -left-[5000px]">
                    <input type="text" name="b_d5c4aef36a582de40d5837112_8fc2472183" tabindex="-1" value="" />
                </div>

                <Button type="submit" size="lg">Subscribe</Button>
            </form>
        </div>
    </div>
</template>
