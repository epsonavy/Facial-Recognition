/**
 * Defines a class for drawing and editing spreadsheets within a tag with
 *
 * Example uses:
 * spreadsheet = new Spreadsheet(some_html_element_id, 
 *     [["Tom",5],["Sally", 6]]); //read-only
 * spreadsheet.draw();
 *
 * spreadsheet2 = new Spreadsheet(some_html_element_id2, 
 *     [["Tom",5],["Sally", 6]], {"mode":"write"}); //editable
 * spreadsheet2.draw();
 *
 * @param String spreadsheet_id the id of the tag in which to draw the
 *      spreadsheet
 * @param Array supplied_data two dimensional array of the rows and columns
 *      of data for the spreadsheet
 */
function Spreadsheet(spreadsheet_id, supplied_data)
{
    var self = this;
    var p = Spreadsheet.prototype;
    var properties = (typeof arguments[2] !== 'undefined') ?
        arguments[2] : {};
    var container = document.getElementById(spreadsheet_id);
    if (!container) {
        return false;
    }
    supplied_data = eval(supplied_data);
    if (!Array.isArray(supplied_data)) {
        supplied_data = [];
    }
    var width = 0;
    for (index in supplied_data) {
        if (!Array.isArray(supplied_data[index])) {
            supplied_data[index] = [];
        }
        if ([index].length > width) {
            width = supplied_data[index].length;
        }
    }
    var length = supplied_data.length;
    var data = [];
    for (var i = 0; i < length; i++) {
        data[i] = [];
        for (var j = 0; j < width; j++) {
            data[i][j] = (typeof supplied_data[i][j] == 'undefined') ? "" :
                supplied_data[i][j];
        }
    }
    var property_defaults = {
        'mode' : 'read', // currently, only supports csv
        'data_id' : spreadsheet_id + "-data",
        'data_name' : 'page',
        'table_style' : 'overflow:auto;height:6in;',
    };
    for (var property_key in property_defaults) {
        if (typeof properties[property_key] !== 'undefined') {
            this[property_key] = properties[property_key];
        } else {
            this[property_key] = property_defaults[property_key];
        }
    }
    /**
     * Main function used to draw the spreadsheet with the container tag
     */
    p.draw = function()
    {
        //used to draw a csv based on spreadsheet data
        var table = "<div style='" + self.table_style + "'>";
        var length = data.length;
        var width = data[0].length;
        var add_button = "";
        var delete_button = "";
        var pre_delete_button = "";
        if (self.mode == 'write') {
        // Original code is here ==========================================================================
            table += "<input id='" + self.data_id+ "' type='hidden' " +
                "name='" + self.data_name + "' value='" + JSON.stringify(
                data)+ "' />";
            add_button = "<button>+</button>";
            pre_delete_button = "<button>-</button>";
        }
        table += "<table border='1' ><tr><th></th>";
        for (var i = 0; i < width; i++) {
            table += "<th style='min-width:1in;text-align:right;'>" +
                delete_button + self.letterRepresentation(i) + add_button +
                "</th>";
            delete_button = pre_delete_button;
        }
        table += "</tr>";
        delete_button = "";
        for (i = 0; i < length; i++) {
            table +="<tr><th style='min-width:1.1in;text-align:right;'>" +
                delete_button + (i + 1) + add_button + "</th>";
            delete_button = pre_delete_button;
            for (var j = 0; j < width; j++) {
                var item = "";
                if (typeof data[i][j] == 'string') {
                    item = data[i][j];
                    if (item.charAt(0) == '=') {
                        item = self.evaluateCell(item.substring(1), 0)[1];
                    }
                }
                table += "<td>" + item + "</td>";
            }
            table += "</tr>";
        }
        table += "</table></div>";
        container.innerHTML = table;
    }

    
    /**
     * Calculates the value of a cell expression in a spreadsheet. Currently,
     * a cell expression is either an integer literal, a non-scientific notation
     * float litera, a cell name literal, or of the form
     * (cell_exp1 op cell_exp2) where cell_exp1 and cell_exp2 are cell
     * expressions that don't evaluate to strings and op is one of +, -, *, /
     * whitespace is ignore in cell expressions
     *
     * @param String cell_expression a string representing a formula to
     * calculate from a spreadsheet file
     * @param Number location character position in cell_expression to start
     *      evaluating from
     * @return mixed the value of the cell or the String 'NaN' if the expression
     *    was not evaluatable
     */
    p.evaluateCell = function(cell_expression, location)
    {
        var out = [location, false];
        if (location >= cell_expression.length) {
            return out;
        }
        location = self.skipWhitespace(cell_expression, location);
        out[0] = location;
        if(cell_expression.charAt(location) == "(") {
            left_out = self.evaluateCell(cell_expression, location + 1);
            if (!['+', '-', '*', '/'].includes(
                cell_expression.charAt(left_out[0])) ||
                typeof left_out[1] == 'String') {
                out[0] = left_out[0];
                out[1] = "NaN";
                return out;
            }
            right_out = self.evaluateCell(cell_expression, left_out[0] + 1);
            if (cell_expression.charAt(right_out[0]) != ')' ||
                typeof right_out[1] == 'String') {
                out[0] = right_out[0];
                out[1] = "NaN";
                return out;
            }
            out[0] = self.skipWhitespace(cell_expression, right_out[0] + 1);
            out[1] = eval("" + left_out[1] +
                cell_expression.charAt(left_out[0]) + right_out[1]);
            return out;
        } else if (cell_expression.charAt(location) == "-") {
            sub_out = self.evaluateCell(cell_expression, location + 1);
            if (sub_out[1] == 'NaN') {
                return sub_out;
            }
            out[0] = self.skipWhitespace(cell_expression, sub_out[0]);
            out[1] = - sub_out[1];
            return out;
        }
        var rest = cell_expression.substring(location);
        var value = rest.match(/^\-?\d+(\.\d*)?|^\-?\.\d+/);
        if (value !== null) {
            out[0] = self.skipWhitespace(cell_expression,location +
                value[0].length +1);
            out[1] = (value[0].match(/\./) == '.') ? parseFloat(value[0]) :
                parseInt(value[0]);
            return out;
        }
        value = rest.match(/^[A-Z]+\d+/);
        if (value !== null) {
            out[0] = self.skipWhitespace(cell_expression,location +
                value.length + 1);
            var row_col = self.cellNameAsRowColumn(value.toString().trim());
            out[1] = data[row_col[0] - 1][row_col[1]];
        }
        return out;
    }
    /**
     * Returns the position of the first non-whitespace character after
     * location in the string (returns location if location is non-WS or
     * if no location found).
     *
     * @param String haystack string to search in
     * @param Number location where to start search from
     * @return Number position of non-WS character
     */
    p.skipWhitespace = function(haystack, location)
    {
        var next_loc = haystack.substring(location).search(/\S/);
        if (next_loc > 0) {
            location += next_loc;
        }
        return location;
    }
    /**
     * Converts a decimal number to a base 26 number string using A-Z for 0-25.
     * Used where drawing column headers for spreadsheet
     * @param Number number the value to convert to base 26
     * @return String result of conversion
     */
    p.letterRepresentation = function(number)
    {
        var pre_letter;
        var out = "";
        do {
            pre_letter = number % 26;
            number = Math.floor(number/26);
            out += String.fromCharCode(65 + pre_letter);
        } while (number > 25);
        return out;
    }
    /**
     * Given a cell name string, such as B4, converts it to an ordered pair
     * suitable for lookup in the spreadsheets data array. On B4,
     * [3, 1] would be returned.
     *
     * @param String cell_name name to convert
     * @return Array ordered pair corresponding to name
     */
    p.cellNameAsRowColumn = function(cell_name)
    {
        var cell_parts = cell_name.match(/^([A-Z]+)(\d+)$/);
        if (cell_parts == null) {
            return null;
        }
        var column_string = cell_parts[1];
        var len = column_string.length;
        var column = 0;
        var shift = 1;
        for (var i = 0; i < len; i++) {
            column += (column_string.charCodeAt(i) - 65) * shift;
            shift = 26;
        }
        return [parseInt(cell_parts[2]), column];
    }
    /**
     * Callback for click events on spreadsheet. Determines if the event
     * occurred on a spreadsheet cell. If so, it opens a prompt for a
     * new value for the cell and 
     s the cell and the associated form
     * hidden input value.
     * @param Object event click event object
     */
    p.updateCell = function (event) {
        var type = (event.target.innerHTML == "+") ? 'add' :
            (event.target.innerHTML == "-") ? 'delete' :'cell';
        var target = (type == 'cell') ? event.target :
            event.target.parentElement;
        var row = target.parentElement.rowIndex - 1;
        var column = target.cellIndex - 1;
        var length = data.length;
        var width = data[0].length;
        if (row >= 0 && column >= 0) {
        	// Original code is here ==========================================================================
        	//var new_value = prompt(self.letterRepresentation(column) +
            //    (row + 1), data[row][column]);
            var new_value = prompt(self.letterRepresentation(column) +
                (row + 1), data[row][column]);
            if (new_value != null) {
                data[row][column] = new_value;
                data_elt = document.getElementById(self.data_id);
                data_elt.value = JSON.stringify(data);
                event.target.innerHTML = new_value;
            }
        } else if (type == 'add' && row == -1 && column >= 0) {
            for (var i = 0; i < length; i++) {
                for (var j = width; j > column + 1; j--) {
                    data[i][j] = data[i][j-1];
                }
                data[i][column + 1] = "";
            }
            data_elt = document.getElementById(self.data_id);
            data_elt.value = JSON.stringify(data);
            self.draw();
        } else if (type == 'add' && row >= 0 && column == -1) {
            data[length] = [];
            for (var i = length; i > row + 1; i--) {
                for (var j = 0; j < width; j++) {
                    data[i][j] = data[i - 1][j];
                }
            }
            for (var j = 0; j < width; j++) {
                data[row + 1][j] = "";
            }
            data_elt = document.getElementById(self.data_id);
            data_elt.value = JSON.stringify(data);
            self.draw();
        } else if (type == 'delete' && row == -1 && column >= 0) {
            for (var i = 0; i < length; i++) {
                for (var j = column ; j < width - 1; j++) {
                    data[i][j] = data[i][j + 1];
                }
                data[i].pop();
            }
            data_elt = document.getElementById(self.data_id);
            data_elt.value = JSON.stringify(data);
            self.draw();
        } else if (type == 'delete' && row >= 0 && column == -1) {
            for (var i = row; i < length - 1; i++) {
                    data[i] = data[i + 1];
            }
            data.pop();
            data_elt = document.getElementById(self.data_id);
            data_elt.value = JSON.stringify(data);
            self.draw();
        }
        event.stopPropagation();
        event.preventDefault();
    }
    if (this.mode == 'write') {
        container.addEventListener("click", self.updateCell, true);
    }
}