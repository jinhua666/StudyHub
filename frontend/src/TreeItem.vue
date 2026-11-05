<script setup lang="ts">
import { ChevronRight, Folder, FolderOpen, Plus } from 'lucide-vue-next'
defineOptions({name:'TreeItem'})
const props=defineProps<{node:any, all:any[], selected:number|null, expanded:Set<number>, depth:number}>()
const emit=defineEmits(['select','toggle','add','move'])
function drop(e:DragEvent) { const id=Number(e.dataTransfer?.getData('text/plain')); const rect=(e.currentTarget as HTMLElement).getBoundingClientRect(); const y=(e.clientY-rect.top)/rect.height; if(id) emit('move',id,props.node.id,y<.25?'before':y>.75?'after':'inside') }
</script>
<template>
  <div class="tree-row" :class="{selected:selected===node.id}" :style="{paddingLeft: `${12 + depth*15}px`}" draggable="true" @dragstart.stop="$event.dataTransfer?.setData('text/plain',String(node.id))" @dragover.prevent @drop.stop.prevent="drop" @click="emit('select',node)">
    <button class="tree-chevron" @click.stop="emit('toggle',node.id)"><ChevronRight :size="14" :class="{rotated:expanded.has(node.id)}" /></button>
    <FolderOpen v-if="expanded.has(node.id)" :size="15" class="tree-folder"/><Folder v-else :size="15" class="tree-folder"/>
    <span class="tree-name">{{node.name}}</span><button class="tree-add" title="新增子分类" @click.stop="emit('add',node)"><Plus :size="14"/></button>
  </div>
  <template v-if="expanded.has(node.id)"><TreeItem v-for="child in all.filter(x=>x.parent_id===node.id)" :key="child.id" :node="child" :all="all" :selected="selected" :expanded="expanded" :depth="depth+1" @select="emit('select',$event)" @toggle="emit('toggle',$event)" @add="emit('add',$event)" @move="(id:number,target:number,position:string)=>emit('move',id,target,position)"/></template>
</template>
