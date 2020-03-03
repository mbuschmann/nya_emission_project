holderbased=20;
holderbasew=22.5;
holderbasetopw=15.5;
holderbaseh=6;

difference(){
union(){
difference(){
translate([holderbased/2-5,0,24]) rotate([0,90,0]) cylinder(d=30, h=10,  center=true, $fn=30);

translate([holderbased/2-5,0,24]) rotate([0,90,0]) cylinder(d=24, h=12,  center=true, $fn=50);
}
translate([holderbased/2-2.5,0,holderbaseh]) cube([5,10,10], center=true);

rotate([0,-90,0])
linear_extrude(height = holderbased, center = true, convexity = 10, twist = 0)
polygon(points = [ [0, -holderbasew/2], [0,holderbasew/2], [holderbaseh,holderbasetopw/2], [holderbaseh,-holderbasetopw/2]]);
}

translate([-8,0,24]) rotate([0,90,0]) cylinder(d=40, h=20,  center=true, $fn=50);

}
