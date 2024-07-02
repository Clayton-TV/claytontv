<!--
  This example requires some changes to your config:
  
  ```
  // tailwind.config.js
  module.exports = {
    // ...
    plugins: [
      // ...
      require('@tailwindcss/forms'),
    ],
  }
  ```
-->
<template>
    <form>
      <div class="space-y-12">
        <div class="border-b border-gray-900/10 pb-12">
            <div class="border-b border-gray-900/10 pb-12">
          <h2 class="text-base font-semibold leading-7 text-gray-900">Update Videos Page</h2>

          <div class="mt-10 grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
            <div class="sm:col-span-4">
              <label for="Demographic" class="block text-sm font-medium leading-6 text-gray-900">Demographic</label>
              <div class="mt-2">
                <div class="flex rounded-md shadow-sm ring-1 ring-inset ring-gray-300 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-600 sm:max-w-md">
                  <span class="flex select-none items-center pl-3 text-gray-500 sm:text-sm">Demographic</span>
                  <input type="text" name="Demographic" id="Demographic" autocomplete="Demographic" class="block flex-1 border-0 bg-transparent py-1.5 pl-1 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm sm:leading-6" placeholder="janesmith" />
                </div>
              </div>
            </div>
  
            <div class="col-span-full">
              <label for="Labels" class="block text-sm font-medium leading-6 text-gray-900">Labels</label>
              <div class="mt-2">
                <textarea id="Labels" name="Labels" rows="3" class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" />
              </div>
              <p class="mt-3 text-sm leading-6 text-gray-600">Labels for the vido</p>
            </div>
            
            <div class="col-span-full">
              <label for="Ministry" class="block text-sm font-medium leading-6 text-gray-900">Ministry</label>
              <div class="mt-2">
                <textarea id="Ministry" name="Ministry" rows="3" class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" />
              </div>
              <p class="mt-3 text-sm leading-6 text-gray-600">Ministry for the vido</p>
            </div>
            
            <div class="sm:col-span-4">
              <label for="Series" class="block text-sm font-medium leading-6 text-gray-900">Series</label>
              <div class="mt-2">
                <div class="flex rounded-md shadow-sm ring-1 ring-inset ring-gray-300 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-600 sm:max-w-md">
                  <span class="flex select-none items-center pl-3 text-gray-500 sm:text-sm">Series</span>
                  <input type="text" name="Series" id="Series" autocomplete="Series" class="block flex-1 border-0 bg-transparent py-1.5 pl-1 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm sm:leading-6" placeholder="janesmith" />
                </div>
              </div>
            </div>

            <div class="sm:col-span-4">
              <label for="Speaker/Artist" class="block text-sm font-medium leading-6 text-gray-900">Speaker/Artist</label>
              <div class="mt-2">
                <div class="flex rounded-md shadow-sm ring-1 ring-inset ring-gray-300 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-600 sm:max-w-md">
                  <span class="flex select-none items-center pl-3 text-gray-500 sm:text-sm">Speaker/Artist</span>
                  <input type="text" name="Speaker/Artist" id="Speaker/Artist" autocomplete="Speaker/Artist" class="block flex-1 border-0 bg-transparent py-1.5 pl-1 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm sm:leading-6" placeholder="janesmith" />
                </div>
              </div>
            </div>
        
            <div class="sm:col-span-4">
              <label for="Bible Books" class="block text-sm font-medium leading-6 text-gray-900">Bible Books</label>
              <div class="mt-2">
                <div class="flex rounded-md shadow-sm ring-1 ring-inset ring-gray-300 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-600 sm:max-w-md">
                  <span class="flex select-none items-center pl-3 text-gray-500 sm:text-sm">Bible Books</span>
                  <input type="text" name="Bible Books" id="Bible Books" autocomplete="Bible Books" class="block flex-1 border-0 bg-transparent py-1.5 pl-1 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm sm:leading-6" placeholder="janesmith" />
                </div>
              </div>
            </div>

            <div class="sm:col-span-4">
              <label for="Date Recorded" class="block text-sm font-medium leading-6 text-gray-900">Date Recorded</label>
              <div class="mt-2">
                <div class="flex rounded-md shadow-sm ring-1 ring-inset ring-gray-300 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-600 sm:max-w-md">
                  <span class="flex select-none items-center pl-3 text-gray-500 sm:text-sm">Date Recorded</span>
                  <input type="text" name="Date Recorded" id="Date Recorded" autocomplete="Date Recorded" class="block flex-1 border-0 bg-transparent py-1.5 pl-1 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm sm:leading-6" placeholder="janesmith" />
                </div>
              </div>
            </div>

            <div class="sm:col-span-4">
              <label for="Date Created" class="block text-sm font-medium leading-6 text-gray-900">Date Created</label>
              <div class="mt-2">
                <div class="flex rounded-md shadow-sm ring-1 ring-inset ring-gray-300 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-600 sm:max-w-md">
                  <span class="flex select-none items-center pl-3 text-gray-500 sm:text-sm">Date Created</span>
                  <input type="text" name="Date Created" id="Date Created" autocomplete="Date Created" class="block flex-1 border-0 bg-transparent py-1.5 pl-1 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm sm:leading-6" placeholder="janesmith" />
                </div>
              </div>
            </div>

            
            <div class="sm:col-span-4">
              <label for="Date Modified" class="block text-sm font-medium leading-6 text-gray-900">Date Modified</label>
              <div class="mt-2">
                <div class="flex rounded-md shadow-sm ring-1 ring-inset ring-gray-300 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-600 sm:max-w-md">
                  <span class="flex select-none items-center pl-3 text-gray-500 sm:text-sm">Date Modified</span>
                  <input type="text" name="Date Modified" id="Date Modified" autocomplete="Date Modified" class="block flex-1 border-0 bg-transparent py-1.5 pl-1 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm sm:leading-6" placeholder="janesmith" />
                </div>
              </div>
            </div>

            
            <div class="sm:col-span-4">
              <label for="Is Livestream" class="block text-sm font-medium leading-6 text-gray-900">Is Livestream</label>
              <div class="mt-2">
                <div class="flex rounded-md shadow-sm ring-1 ring-inset ring-gray-300 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-600 sm:max-w-md">
                  <span class="flex select-none items-center pl-3 text-gray-500 sm:text-sm">Is Livestream</span>
                  <input type="text" name="Is Livestream" id="Is Livestream" autocomplete="Is Livestream" class="block flex-1 border-0 bg-transparent py-1.5 pl-1 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm sm:leading-6" placeholder="janesmith" />
                </div>
              </div>
            </div>
            
            <div class="sm:col-span-4">
              <label for="Channel" class="block text-sm font-medium leading-6 text-gray-900">Channel</label>
              <div class="mt-2">
                <div class="flex rounded-md shadow-sm ring-1 ring-inset ring-gray-300 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-600 sm:max-w-md">
                  <span class="flex select-none items-center pl-3 text-gray-500 sm:text-sm">Channel</span>
                  <input type="text" name="Channel" id="Channel" autocomplete="Channel" class="block flex-1 border-0 bg-transparent py-1.5 pl-1 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm sm:leading-6" placeholder="janesmith" />
                </div>
              </div>
            </div>
            
            <div class="sm:col-span-4">
              <label for="Topic" class="block text-sm font-medium leading-6 text-gray-900">Topic</label>
              <div class="mt-2">
                <div class="flex rounded-md shadow-sm ring-1 ring-inset ring-gray-300 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-600 sm:max-w-md">
                  <span class="flex select-none items-center pl-3 text-gray-500 sm:text-sm">Topic</span>
                  <input type="text" name="Topic" id="Topic" autocomplete="Topic" class="block flex-1 border-0 bg-transparent py-1.5 pl-1 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm sm:leading-6" placeholder="janesmith" />
                </div>
              </div>
            </div>
          </div>
        </div>
  
        <div class="border-b border-gray-900/10 pb-12">
          <h2 class="text-base font-semibold leading-7 text-gray-900">Labels</h2>
          <p class="mt-1 text-sm leading-6 text-gray-600">Labels for the video.</p>
          
          <div class="sm:col-span-4">
              <label for="Series" class="block text-sm font-medium leading-6 text-gray-900">Series</label>
              <div class="mt-2">
                <div class="flex rounded-md shadow-sm ring-1 ring-inset ring-gray-300 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-600 sm:max-w-md">
                  <span class="flex select-none items-center pl-3 text-gray-500 sm:text-sm">Series</span>
                  <input type="text" name="Series" id="Series" autocomplete="Series" class="block flex-1 border-0 bg-transparent py-1.5 pl-1 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm sm:leading-6" placeholder="janesmith" />
                </div>
              </div>
            </div>
            
            <div class="sm:col-span-4">
              <label for="Subseries" class="block text-sm font-medium leading-6 text-gray-900">Subseries</label>
              <div class="mt-2">
                <div class="flex rounded-md shadow-sm ring-1 ring-inset ring-gray-300 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-600 sm:max-w-md">
                  <span class="flex select-none items-center pl-3 text-gray-500 sm:text-sm">Subseries</span>
                  <input type="text" name="Subseries" id="Subseries" autocomplete="Subseries" class="block flex-1 border-0 bg-transparent py-1.5 pl-1 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm sm:leading-6" placeholder="janesmith" />
                </div>
              </div>
            </div>

            <div class="sm:col-span-4">
              <label for="Episodes" class="block text-sm font-medium leading-6 text-gray-900">Episodes</label>
              <div class="mt-2">
                <div class="flex rounded-md shadow-sm ring-1 ring-inset ring-gray-300 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-600 sm:max-w-md">
                  <span class="flex select-none items-center pl-3 text-gray-500 sm:text-sm">Episodes</span>
                  <input type="text" name="Episodes" id="Episodes" autocomplete="Episodes" class="block flex-1 border-0 bg-transparent py-1.5 pl-1 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm sm:leading-6" placeholder="janesmith" />
                </div>
              </div>
            </div>

        </div> 
  
        <div class="border-b border-gray-900/10 pb-12">
    
          <h2 class="text-base font-semibold leading-7 text-gray-900">Topic</h2>
          <p class="mt-1 text-sm leading-6 text-gray-600">We'll always let you know about important changes, but you pick what else you want to hear about.</p>

        </div>  

        <div class="border-b border-gray-900/10 pb-12">
          <h2 class="text-base font-semibold leading-7 text-gray-900">Speaker/Artist</h2>
          <p class="mt-1 text-sm leading-6 text-gray-600">We'll always let you know about important changes, but you pick what else you want to hear about.</p>

        </div> 

        <div class="border-b border-gray-900/10 pb-12">
          <h2 class="text-base font-semibold leading-7 text-gray-900">Channel</h2>
          <p class="mt-1 text-sm leading-6 text-gray-600">We'll always let you know about important changes, but you pick what else you want to hear about.</p>

        </div> 

        <div class="border-b border-gray-900/10 pb-12">
          <h2 class="text-base font-semibold leading-7 text-gray-900">Series</h2>
          <p class="mt-1 text-sm leading-6 text-gray-600">We'll always let you know about important changes, but you pick what else you want to hear about.</p>

        </div> 

        <div class="border-b border-gray-900/10 pb-12">
          <h2 class="text-base font-semibold leading-7 text-gray-900">Bible Book</h2>
          <p class="mt-1 text-sm leading-6 text-gray-600">We'll always let you know about important changes, but you pick what else you want to hear about.</p>

        </div> 

        <div class="border-b border-gray-900/10 pb-12">
          <h2 class="text-base font-semibold leading-7 text-gray-900">Ministry</h2>
          <p class="mt-1 text-sm leading-6 text-gray-600">We'll always let you know about important changes, but you pick what else you want to hear about.</p>

        </div>

        <div class="border-b border-gray-900/10 pb-12">
          <h2 class="text-base font-semibold leading-7 text-gray-900">Demographic</h2>
          <p class="mt-1 text-sm leading-6 text-gray-600">We'll always let you know about important changes, but you pick what else you want to hear about.</p>

        </div>


     </div>
    </div>
      <div class="mt-6 flex items-center justify-end gap-x-6">
        <button type="button" class="text-sm font-semibold leading-6 text-gray-900">Cancel</button>
        <button type="submit" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">Save</button>
      </div>
    </form>
  </template>
  
  <script setup>
  import { PhotoIcon, UserCircleIcon } from '@heroicons/vue/24/solid'

  </script>