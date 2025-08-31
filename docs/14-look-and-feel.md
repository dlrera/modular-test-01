# Look and Feel Guide

## Overview
This guide establishes the visual design standards and UI patterns for the Property Management application, based on the proven design system from the Fleet Management application. Following these guidelines ensures a consistent, professional user experience across all modules.

## Design Framework

### Core Technology Stack
- **UI Framework**: Vuetify 3.5+
- **Icons**: Material Design Icons (@mdi/font)
- **CSS Preprocessor**: Sass
- **Component Pattern**: Vue 3 Composition API with `<script setup>`

## Color Palette

### Primary Colors
```scss
$primary: #216093;      // Blue - Primary actions, headers
$secondary: #001B48;    // Navy Blue - Navigation, emphasis
$accent: #57949A;       // Teal - Highlights, secondary actions
```

### System Colors
```scss
$error: #DB162F;        // Red - Errors, deletions
$success: #2E933C;      // Green - Success states, confirmations
$warning: #E18331;      // Orange - Warnings, attention needed
$info: #224870;         // Medium Blue - Information, notices
```

### Background Colors
```scss
$background: #F9FAFA;   // Light Gray - Main background
$surface: #FFFFFF;      // White - Cards, panels
$on-background: #000000;  // Black - Text on background
$on-surface: #000000;    // Black - Text on surface
```

## Typography

### Heading Hierarchy
- **Page Title**: `text-h5 font-weight-medium` 
- **Section Header**: `text-h6 font-weight-medium`
- **Card Title**: `text-h6` or `text-subtitle-1 font-weight-medium`
- **Subtitle**: `text-body-2 text-medium-emphasis`

### Text Styling
- **Body Text**: Default Vuetify body text
- **Help Text**: `text-body-2 text-medium-emphasis`
- **Captions**: `text-caption text-medium-emphasis`
- **Error Messages**: `text-error text-body-2`

## Component Patterns

### Page Layout Structure
```vue
<template>
  <v-container fluid>
    <!-- Page Header -->
    <v-row class="mb-3">
      <v-col cols="12" md="8">
        <h1 class="text-h5 font-weight-medium mb-1">
          [Module Name] Management
        </h1>
        <p class="text-body-2 text-medium-emphasis">
          [Brief description of module purpose]
        </p>
      </v-col>
      <v-col cols="12" md="4" class="text-md-right">
        <!-- Action buttons -->
      </v-col>
    </v-row>
    
    <!-- Main Content -->
    <!-- ... -->
  </v-container>
</template>
```

### Navigation Drawer
- **Background**: `color="secondary"` (Navy Blue)
- **Text**: White with `style="color: white !important;"`
- **Icons**: Material Design Icons with descriptive names
- **Active State**: `color="primary"`
- **Dividers**: Between logical sections

### Cards
```vue
<v-card>
  <v-card-title class="text-h6">
    Card Title
  </v-card-title>
  <v-card-text>
    <p class="text-body-2 text-medium-emphasis mb-4">
      Description or help text
    </p>
    <!-- Content -->
  </v-card-text>
  <v-card-actions>
    <!-- Action buttons -->
  </v-card-actions>
</v-card>
```

### Forms

#### Input Fields
```vue
<v-text-field
  v-model="form.fieldName"
  label="Field Label"
  variant="outlined"
  :rules="[rules.required]"
  class="mb-4"
/>
```

#### Select Dropdowns
```vue
<v-select
  v-model="form.selectField"
  :items="options"
  label="Select Label"
  variant="outlined"
  :rules="[rules.required]"
  class="mb-4"
/>
```

#### Form Actions
```vue
<div class="d-flex ga-4">
  <v-btn variant="outlined" @click="handleCancel">
    Cancel
  </v-btn>
  <v-btn color="primary" type="submit" :loading="loading">
    Submit
  </v-btn>
</div>
```

### Buttons

#### Primary Actions
```vue
<v-btn color="primary" prepend-icon="mdi-plus">
  Add Item
</v-btn>
```

#### Secondary Actions
```vue
<v-btn variant="outlined" prepend-icon="mdi-file-upload">
  Import
</v-btn>
```

#### Icon Buttons
```vue
<v-btn icon size="small">
  <v-icon>mdi-pencil</v-icon>
</v-btn>
```

### Data Tables
```vue
<v-data-table
  :headers="headers"
  :items="items"
  :loading="loading"
  class="elevation-1"
>
  <template v-slot:item.actions="{ item }">
    <v-btn icon size="small" @click="editItem(item)">
      <v-icon>mdi-pencil</v-icon>
    </v-btn>
    <v-btn icon size="small" @click="deleteItem(item)">
      <v-icon>mdi-delete</v-icon>
    </v-btn>
  </template>
</v-data-table>
```

### Statistics Cards
```vue
<div class="stat-card pa-3 cursor-pointer">
  <div class="d-flex align-center">
    <div class="flex-grow-1">
      <div class="text-h6 font-weight-medium">
        {{ statValue }}
      </div>
      <div class="text-caption text-medium-emphasis">
        Stat Label
      </div>
    </div>
    <v-icon size="24" class="text-medium-emphasis">
      mdi-icon-name
    </v-icon>
  </div>
</div>
```

### Modals/Dialogs
```vue
<v-dialog v-model="showDialog" max-width="600">
  <v-card>
    <v-card-title class="text-h5 bg-primary text-white">
      Dialog Title
    </v-card-title>
    <v-card-text class="pt-6">
      <!-- Content -->
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn variant="text" @click="showDialog = false">
        Cancel
      </v-btn>
      <v-btn color="primary" variant="elevated" @click="handleConfirm">
        Confirm
      </v-btn>
    </v-card-actions>
  </v-card>
</v-dialog>
```

## Spacing Guidelines

### Container Spacing
- **Fluid containers**: Use `<v-container fluid>` for full-width layouts
- **Page sections**: `mb-3` or `mb-4` between major sections
- **Card spacing**: Default Vuetify spacing

### Form Spacing
- **Between fields**: `class="mb-4"`
- **Button groups**: `class="d-flex ga-4"`
- **Section dividers**: `<v-divider class="my-4">`

### Padding Standards
- **Card content**: `pa-3` to `pa-8` depending on content density
- **Compact lists**: `density="compact"`
- **Button padding**: Use Vuetify size props (`size="small"`, `size="large"`)

## User Feedback

### Loading States
```vue
<v-btn :loading="loading" :disabled="loading">
  Action
</v-btn>

<v-progress-linear v-if="loading" indeterminate color="primary" />
```

### Snackbar Notifications
```vue
<v-snackbar
  v-model="snackbar.show"
  :color="snackbar.color"
  :timeout="3000"
  location="top right"
>
  {{ snackbar.message }}
  <template v-slot:actions>
    <v-btn variant="text" @click="snackbar.show = false">
      Close
    </v-btn>
  </template>
</v-snackbar>
```

### Alert Messages
```vue
<v-alert
  type="error"
  variant="tonal"
  closable
  class="mb-4"
>
  Error message here
</v-alert>
```

## Responsive Design

### Breakpoint Usage
- **Mobile**: `cols="12"`
- **Tablet**: `sm="6"` or `sm="8"`
- **Desktop**: `md="4"`, `md="6"`, `md="8"`
- **Large Desktop**: `lg="3"`, `lg="4"`, `lg="6"`

### Mobile Considerations
- **Navigation**: Collapsible drawer with hamburger menu
- **Tables**: Horizontal scroll or card view on mobile
- **Button text**: Hide on small screens using `class="d-none d-sm-inline"`
- **Alignment**: Use `text-md-right` for responsive alignment

## Icon Guidelines

### Common Icon Mappings
- **Add/Create**: `mdi-plus`
- **Edit**: `mdi-pencil`
- **Delete**: `mdi-delete`
- **Save**: `mdi-content-save`
- **Cancel**: `mdi-close`
- **Search**: `mdi-magnify`
- **Filter**: `mdi-filter`
- **Export**: `mdi-download`
- **Import**: `mdi-upload`
- **Settings**: `mdi-cog`
- **User**: `mdi-account`
- **Calendar**: `mdi-calendar`
- **Document**: `mdi-file-document`
- **Building**: `mdi-office-building`
- **Home**: `mdi-home`
- **Money**: `mdi-currency-usd`

## Authentication Pages

### Login Page Style
- **Background**: Gradient from primary to secondary
- **Card**: Elevated with rounded corners
- **Header**: Primary background with white text
- **Form**: Outlined variants with primary color focus

## Best Practices

### Consistency Rules
1. Always use outlined variant for form inputs
2. Primary buttons for main actions, outlined for secondary
3. Consistent spacing using Vuetify utility classes
4. Use text emphasis classes for secondary text
5. Maintain icon consistency across similar actions

### Accessibility
1. Include `aria-label` on icon-only buttons
2. Use semantic HTML structure
3. Maintain sufficient color contrast
4. Provide loading and error states
5. Include keyboard navigation support

### Performance
1. Lazy load heavy components
2. Use virtual scrolling for long lists
3. Implement proper loading states
4. Debounce search inputs (300ms)
5. Optimize images and assets

## Module-Specific Styling

When creating new modules, maintain consistency while allowing for module-specific needs:

1. **Use the established color palette** - Don't introduce new colors without updating this guide
2. **Follow component patterns** - Reuse established patterns before creating new ones
3. **Maintain spacing consistency** - Use the same spacing utilities throughout
4. **Icon selection** - Choose icons that align with existing usage patterns
5. **Form validation** - Use consistent validation rules and error display

## Testing Visual Consistency

Before deploying new features:
1. Compare with existing modules for visual consistency
2. Test responsive behavior at all breakpoints
3. Verify color contrast meets accessibility standards
4. Ensure loading states are properly implemented
5. Check that all interactive elements have appropriate feedback

---

This guide should be treated as a living document and updated as the design system evolves. All developers should familiarize themselves with these patterns to maintain a cohesive user experience across the application.