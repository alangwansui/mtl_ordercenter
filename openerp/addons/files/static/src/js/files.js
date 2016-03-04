
openerp.files = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.files = {};

instance.files.filesname = instance.web.form.AbstractField.extend({
		
			init: function() {
				this._super.apply(this, arguments);
				this.set("value", "");
			},
			start: function() {
				this.on("change:effective_readonly", this, function() {
					this.display_field();
					this.render_value();
				});
				this.display_field();
				return this._super();
			},
			display_field: function() {
				var self = this;
				this.$el.html(QWeb.render("files", {widget: this}));				
			
				if (! this.get("effective_readonly")){
				
               	this.$(".files").change(function() {
                    var filePath=$(this).val();
                    var model = new instance.web.Model("files_name");
                    model.call("write", [self.view.datarecord.id,{"message":filePath}], {context: new instance.web.CompoundContext()}).then();
                 // self.$(".oe-field-input-55").val(filePath);
                  //  alert(self.view.datarecord.id);
                });
                 } 
			},

		
	  
});
 instance.web.form.widgets.add('files', 'instance.files.filesname');
}
