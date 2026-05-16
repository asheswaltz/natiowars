/**
 * WytopiaSDK – stub autonome
 * Permet de lancer le jeu sans la plateforme Wytopia.
 * - Lit ?level= et ?lang= dans l'URL pour compatibilité.
 * - levelComplete() renvoie une Promise avec le niveau suivant.
 */
(function (global) {
  'use strict';

  function WytopiaSDK(options) {
    this._logging = !!(options && options.logging);
    this._gameCompletedCallbacks = [];

    // Lecture des paramètres URL
    var params = new URLSearchParams(global.location.search);
    var lvlParam = parseInt(params.get('level'), 10);
    this._startLevel = (lvlParam >= 1) ? lvlParam : 1;

    var langParam = params.get('lang');
    if (langParam) {
      this._lang = langParam;
    }

    if (this._logging) {
      console.log('[WytopiaSDK stub] initialisé – startLevel=' + this._startLevel);
    }
  }

  /** Retourne le niveau de départ fourni par l'URL (?level=N) ou 1. */
  WytopiaSDK.prototype.getStartLevel = function () {
    return this._startLevel;
  };

  /** Enregistre un callback appelé quand le jeu est terminé. */
  WytopiaSDK.prototype.onGameCompleted = function (callback) {
    if (typeof callback === 'function') {
      this._gameCompletedCallbacks.push(callback);
    }
  };

  /**
   * Notifie la complétion d'un niveau.
   * @param {number} level  - numéro du niveau complété
   * @param {object} data   - { grade, duration }
   * @returns {Promise<{level: number}>} – niveau suivant conseillé
   */
  WytopiaSDK.prototype.levelComplete = function (level, data) {
    if (this._logging) {
      console.log('[WytopiaSDK stub] levelComplete – level=' + level, data);
    }
    // En mode standalone : niveau suivant = level + 1
    return Promise.resolve({ level: level + 1 });
  };

  /** Déclenche manuellement les callbacks onGameCompleted (usage interne). */
  WytopiaSDK.prototype._triggerGameCompleted = function () {
    this._gameCompletedCallbacks.forEach(function (cb) { cb(); });
  };

  global.WytopiaSDK = WytopiaSDK;
}(window));
