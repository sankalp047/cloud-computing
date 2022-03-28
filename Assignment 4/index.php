<?php
use Phppot\DataSource;

require_once 'DataSource.php';
$db = new DataSource();
$conn = $db->getConnection();

if (isset($_POST["import"])) {
    
    $fileName = $_FILES["file"]["tmp_name"];
    
    if ($_FILES["file"]["size"] > 0) {
        
        $file = fopen($fileName, "r");
        while (($column = fgetcsv($file, 10000, ",")) !== FALSE) {
            
            $name= "";
            if (isset($column[0])) {
                $name = mysqli_real_escape_string($conn, $column[0]);
            }
            $id = "";
            if (isset($column[1])) {
                $id = mysqli_real_escape_string($conn, $column[1]);
            }
            
          
//SELECT job FROM mytable WHERE id IN (10..15);
            $sqlSearch = "SELECT name FROM ni WHERE id IN (<?php $id1..$id2?>))";
            
            if (! empty($insertId)) {
                $type = "success";
                $message = "Result:-";
            } else {
                $type = "error";
                $message = "Problem fetchinh data";
            }
        }
    }
}
?>
<!DOCTYPE html>
<html>

<head>
<script src="jquery-3.2.1.min.js"></script>

<style>
body {
    font-family: Arial;
    width: 550px;
}

.outer-scontainer {
    background: #F0F0F0;
    border: #e0dfdf 1px solid;
    padding: 20px;
    border-radius: 2px;
}

.input-row {
    margin-top: 0px;
    margin-bottom: 20px;
}

.btn-submit {
    background: #333;
    border: #1d1d1d 1px solid;
    color: #f0f0f0;
    font-size: 0.9em;
    width: 100px;
    border-radius: 2px;
    cursor: pointer;
}

.outer-scontainer table {
    border-collapse: collapse;
    width: 100%;
}

.outer-scontainer th {
    border: 1px solid #dddddd;
    padding: 8px;
    text-align: left;
}

.outer-scontainer td {
    border: 1px solid #dddddd;
    padding: 8px;
    text-align: left;
}

#response {
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 2px;
    display: none;
}

.success {
    background: #c7efd9;
    border: #bbe2cd 1px solid;
}

.error {
    background: #fbcfcf;
    border: #f3c6c7 1px solid;
}

div#response.display-block {
    display: block;
}
</style>
<script type="text/javascript">
$(document).ready(function() {
    $("#frmCSVImport").on("submit", function () {

	    $("#response").attr("class", "");
        $("#response").html("");
        var fileType = ".csv";
        var regex = new RegExp("([a-zA-Z0-9\s_\\.\-:])+(" + fileType + ")$");
        if (!regex.test($("#file").val().toLowerCase())) {
        	    $("#response").addClass("error");
        	    $("#response").addClass("display-block");
            $("#response").html("Invalid File. Upload : <b>" + fileType + "</b> Files.");
            return false;
        }
        return true;
    });
});
</script>
</head>

<body>
	<h3>Sankalp Sandeep Singh<br> UTA - 1001964065</h3>
    <h2>Finding data in range</h2>

    <div id="response"
        class="<?php if(!empty($type)) { echo $type . " display-block"; } ?>">
        <?php if(!empty($message)) { echo $message; } ?>
        </div>
    <div class="outer-scontainer">
        <div class="row">

            <form class="form-horizontal" action="" method="post"
                name="frmCSVImport" id="frmCSVImport"
                enctype="multipart/form-data">
                <div class="input-row">
                    <label class="col-md-4 control-label"></label> <input type="text" name="id2"
                        id="file">
			<label class="col-md-4 control-label"></label> <input type="text" name="id2"
                        id="file">
                    <button type="submit" id="submit" name="import"
                        class="btn-submit">Search</button>
                    <br />

                </div>

            </form>
		

        </div>
               <?php
            $sqlSelect = "SELECT name FROM ni WHERE id BETWEEN 5000 and 7000";;
	    //SELECT job FROM mytable WHERE id BETWEEN 10 AND 15
            $result = $db->select($sqlSelect);
            if (! empty($result)) {
                ?>
            <table id='ni'>
            <thead>
                <tr>
			<th>name</th>
			<th>id</th>

                </tr>
            </thead>
<?php
                
                foreach ($result as $row) {
                    ?>
                    
                <tbody>
                <tr>
                    <td><?php  echo $row['name']; ?></td>
                    <td><?php  echo $row['id']; ?></td>
                   
                </tr>
                    <?php
                }
                ?>
                </tbody>
        </table>
        <?php } ?>
    </div>

</body>
</html>
