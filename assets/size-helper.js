/*
 * <size-helper> — minimalist size-recommendation widget shown above the
 * "Largeur" variant picker on products whose size option values end in "mm".
 *
 * Business rule (unchanged): the mount holds the gear by its edges, so the wide
 * part (ski tip / snowboard nose) must be WIDER than the mount. We recommend the
 * largest size that still stays narrower than the measured width, minus a margin.
 *
 * Wiring (unchanged): clicking the recommended size checks the matching radio in
 * the existing <variant-selector> and dispatches a bubbling "change" event, so
 * the native picker updates price / availability / ?variant= / add-to-cart.
 */
(function () {
  if (customElements.get('size-helper')) return;

  class SizeHelper extends HTMLElement {
    connectedCallback() {
      if (this.dataset.ready) return; // guard against double init
      this.dataset.ready = '1';

      const sizesEl = this.querySelector('.size-helper__sizes');
      let raw = [];
      try {
        raw = JSON.parse(sizesEl ? sizesEl.textContent : '[]');
      } catch (e) {
        raw = [];
      }
      this.sizes = raw
        .map((v) => parseInt(String(v).replace(/[^0-9.-]/g, ''), 10))
        .filter((n) => !isNaN(n))
        .sort((a, b) => a - b);

      if (this.sizes.length === 0) {
        this.hidden = true;
        return;
      }

      this.margin = parseInt(this.getAttribute('data-margin'), 10);
      if (isNaN(this.margin)) this.margin = 6;
      this.labelCheck = this.getAttribute('data-label-check') || '';
      this.labelIdeal = this.getAttribute('data-label-ideal') || '';

      this.range = this.querySelector('.size-helper__range');
      this.num = this.querySelector('.size-helper__num');
      this.reco = this.querySelector('.size-helper__reco');
      this.recoValue = this.querySelector('.size-helper__reco-value');
      this.info = this.querySelector('.size-helper__info');
      this.tooltip = this.querySelector('.size-helper__tooltip');
      this.selector = document.querySelector('variant-selector');

      const bounds = this.computeBounds();
      this.min = bounds.min;
      this.max = bounds.max;
      this.range.min = this.min;
      this.range.max = this.max;
      this.num.min = this.min;
      this.num.max = this.max;

      this.current = null;

      this.range.addEventListener('input', () => this.update(+this.range.value));
      this.num.addEventListener('input', () => {
        if (this.num.value !== '') this.update(+this.num.value);
      });
      this.num.addEventListener('blur', () => this.update(+this.num.value));
      this.recoValue.addEventListener('click', (e) => {
        e.preventDefault();
        this.choose();
      });

      this.bindTooltip();
      this.update(Math.round((this.min + this.max) / 2));
    }

    /* ---- ⓘ tooltip: click to open, Esc / outside click to close ---- */
    bindTooltip() {
      if (!this.info || !this.tooltip) return;
      this.info.addEventListener('click', (e) => {
        e.stopPropagation();
        this.toggleTip();
      });
      this.onDocClick = (e) => {
        if (!this.contains(e.target)) this.closeTip();
      };
      this.onKey = (e) => {
        if (e.key === 'Escape') this.closeTip();
      };
      document.addEventListener('click', this.onDocClick);
      document.addEventListener('keydown', this.onKey);
    }

    toggleTip() {
      if (this.tooltip.hidden) this.openTip();
      else this.closeTip();
    }

    openTip() {
      this.tooltip.hidden = false;
      this.info.setAttribute('aria-expanded', 'true');
    }

    closeTip() {
      if (!this.tooltip) return;
      this.tooltip.hidden = true;
      this.info.setAttribute('aria-expanded', 'false');
    }

    disconnectedCallback() {
      if (this.onDocClick) document.removeEventListener('click', this.onDocClick);
      if (this.onKey) document.removeEventListener('keydown', this.onKey);
    }

    computeBounds() {
      const s = this.sizes;
      const step = s.length > 1 ? (s[s.length - 1] - s[0]) / (s.length - 1) : 15;
      return { min: s[0], max: Math.round(s[s.length - 1] + step) };
    }

    recommend(w) {
      let best = null;
      for (let i = 0; i < this.sizes.length; i++) {
        const sz = this.sizes[i];
        if (sz <= w - this.margin && (best === null || sz > best)) best = sz;
      }
      return best;
    }

    update(w) {
      w = Math.round(w);
      if (isNaN(w)) w = this.min;
      if (w < this.min) w = this.min;
      if (w > this.max) w = this.max;
      this.range.value = w;
      this.num.value = w;

      const pct = ((w - this.min) / (this.max - this.min)) * 100;
      this.range.style.setProperty('--sh-fill', pct + '%');

      const r = this.recommend(w);
      this.current = r;
      if (r !== null) {
        this.reco.classList.remove('size-helper__reco--bad');
        this.recoValue.textContent = r + ' mm';
        this.recoValue.disabled = false;
      } else {
        this.reco.classList.add('size-helper__reco--bad');
        this.recoValue.textContent = this.labelCheck;
        this.recoValue.disabled = true;
      }
      this.markReco(r);
    }

    swatches() {
      if (!this.selector) return [];
      return Array.from(this.selector.querySelectorAll('.product__swatch'));
    }

    swatchSize(label) {
      const input = label.querySelector('input[type="radio"]');
      if (!input) return null;
      const v = (input.value || '').trim();
      if (!/mm\s*$/i.test(v)) return null;
      const n = parseInt(v.replace(/[^0-9.-]/g, ''), 10);
      return isNaN(n) ? null : n;
    }

    markReco(r) {
      this.swatches().forEach((label) => {
        const n = this.swatchSize(label);
        const existing = label.querySelector('.size-helper-badge');
        if (r !== null && n === r) {
          label.classList.add('size-helper-reco');
          if (this.labelIdeal && !existing) {
            const b = document.createElement('span');
            b.className = 'size-helper-badge';
            b.textContent = this.labelIdeal;
            b.setAttribute('aria-hidden', 'true');
            label.appendChild(b);
          }
        } else {
          label.classList.remove('size-helper-reco');
          if (existing) existing.remove();
        }
      });
    }

    choose() {
      if (this.current === null || !this.selector) return;
      const target = this.swatches().find((label) => this.swatchSize(label) === this.current);
      if (!target) return;
      const input = target.querySelector('input[type="radio"]');
      if (!input) return;
      if (!input.checked) {
        input.checked = true;
        input.dispatchEvent(new Event('change', { bubbles: true }));
      }
    }
  }

  customElements.define('size-helper', SizeHelper);
})();
